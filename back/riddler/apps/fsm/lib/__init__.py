import asyncio

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.forms import model_to_dict
from typing import List, NamedTuple, Text
from rest_framework.request import Request

from riddler.apps.broker.models.message import Message
from logging import getLogger
from riddler.utils import WSStatusCodes

logger = getLogger(__name__)


class State(NamedTuple):
    """
    Attributes
    ----------
    name: str
        A human readable name for describing the state
    events: List of str
        A list of strings which are the function's names needed to be executed right after we enter the state
    initial: bool
        It defines the initial state, there should only be 1
    """
    name: Text
    events: List[Text] = []
    initial: bool = False
    ubiquitous: bool = False


class Transition(NamedTuple):
    """
    Attributes
    ----------
    source: str
        'from' state
        If source = None then it describes a state that can be accessed from any other state,
        referred as an 'ubiquitous state'.
    dest: str
        'to' state
    conditions: List of str
        A list of strings which are the function's names needed to be executed to determine if we can enter the 'dest'
        state
    unless: List of str
        The same as conditions but considering the function with a 'not' operator in front of it
    """
    dest: Text
    source: Text = None
    conditions: List[Text] = []
    unless: List[Text] = []


class FSMContext:
    """
    Abstract class all http views/WS representing a bot should inherit from,
    this way we have a generic and shared functionality across the different
    bots whatever what kind they are (WebSocket based, http views and what not)
    making the FSM states access to this 'connection' functionality
    """
    def __init__(self, *args, **kargs):
        from riddler.apps.broker.models.platform_config import PlatformConfig # TODO: fix CI
        self.conversation_id: str = None
        self.platform_config: PlatformConfig = None
        super().__init__(*args, **kargs)

    async def send_response(self, *args, **kargs):
        raise NotImplementedError(
            "All classes that behave as contexts for machines should implement 'send_response'"
        )

    def gather_platform_config(self, request: Request = None):
        raise NotImplemented("Implement a method that gathers the fsm name")

    def gather_conversation_id(self, mml: Message = None):
        raise NotImplemented("Implement a method that gathers the conversation id")

    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id

    def set_platform_config(self, platform_config):
        self.platform_config = platform_config

    async def get_last_mml(
        self,
    ) -> Message:
        return await sync_to_async(
            Message.objects.filter(conversation=self.conversation_id)
            .order_by("-created_date")
            .first
        )()

    async def serialize(self):
        """
        We serialize the ctx just so we can send it to the RPC Servers
        """
        last_mml = model_to_dict((await self.get_last_mml()), fields=["stacks"])
        return {
            "conversation_id": self.conversation_id,
            "last_mml": last_mml,
        }


class FSM:
    """
    FSM as in "Finite-State Machine".
    Bots are represented as a FSM: states are the various states of the bot.
    """
    channel_layer = get_channel_layer()

    def __init__(
        self,
        ctx: FSMContext,
        states: List[State],
        transitions: List[Transition],
        current_state: State = None,
    ):
        """
        Parameters
        ----------
        ctx
            The connextion context, usually useful to get the MML which triggered the state
        states
            States usually sends messages to the user.
        transitions
            Contain the handlers and information that determines state changes.
        current_state
            It will usually be None when a new conversation a thus a new FSM starts. If the FSM come from a CachedFSM
            then it is when current_state is set to the cached current_state
        """
        self.ctx = ctx
        self.states = states
        self.transitions = transitions
        self.rpc_result_future: asyncio.Future = None

        self.current_state = current_state
        if not current_state:
            self.current_state = self.get_initial_state()

    async def start(self):
        await self.run_current_state_events()
        logger.debug(f"FSM start --> {self.current_state}")
        await self.save_cache()

    async def next_state(self):
        """
        It will cycle to the next state based on which transition returns a higher probability, once the next state
        is reached it makes sure everything is saved and cached into the DB to keep the system stateful
        """
        transitions = self.get_current_state_transitions()
        best_score = 0
        best_transition = None
        transition_data = {}
        for t in transitions:
            score, _data = await self.check_transition_condition(t)
            if score > best_score:
                best_transition = t
                best_score = score
                transition_data = _data
        if best_transition:
            logger.debug(f"FSM from ---> {self.current_state}")
            self.current_state = self.get_state_by_name(best_transition.dest)
            logger.debug(f"FSM to -----> {self.current_state}")
            await self.run_current_state_events(transition_data)
        await self.save_cache()

    async def run_current_state_events(self, transition_data={}):
        for event in self.current_state.events:
            await getattr(self.ctx, event)(transition_data)  # call run_condition and wait

    def get_initial_state(self):

        for state in self.states:
            if state.initial:
                return state
        raise Exception("There must be an initial state")

    def get_state_by_name(self, name):
        for state in self.states:
            if state.name == name:
                return state

    def get_current_state_transitions(self):
        return filter(lambda t: t.source == self.current_state.name or t.source is None, self.transitions)

    async def check_transition_condition(self, transition):
        """
        For a transition it will compute its score based on all its conditions
        """
        max_score = 0 if transition.conditions else 1
        data = {}
        for condition_name in transition.conditions:
            score, _data = await self.run_condition(condition_name)
            if score > max_score:
                max_score = score
                data = _data

        un_max_score = 0
        for condition_name in transition.unless:
            score, _ = await self.run_condition(condition_name)
            if score > un_max_score:
                un_max_score = score

        return max_score - un_max_score, data

    async def run_condition(self, condition_name):
        """
        It will call the RPC server, 'condition_name' is the procedure the remote server should run
        Then it will wait util the response is back into the databse
        Parameters
        ----------
        condition_name: str
            Name of the remote procedure to call

        Returns
        -------
        tuple[float, dict]
            The first float indicates the score, the returning dictionary is the result of the RPC

        """
        from riddler.apps.broker.consumers.rpc_consumer import RPCConsumer  # TODO: fix CI

        group_name = RPCConsumer.create_group_name(self.ctx.platform_config.fsm_def_id)
        data = {
            "type": "response",
            "status": WSStatusCodes.ok.value,
            "payload": {
                "name": condition_name,
                "ctx": await self.ctx.serialize()
            }
        }
        await self.channel_layer.group_send(group_name, data)
        self.rpc_result_future = asyncio.get_event_loop().create_future()
        payload = await self.rpc_result_future
        return payload["score"], payload["data"]

    async def save_cache(self):
        from riddler.apps.fsm.models import CachedFSM  # TODO: Resolve CI

        await sync_to_async(CachedFSM.update_or_create)(self)
