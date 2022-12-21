from typing import Coroutine, List, NamedTuple, Text

from asgiref.sync import sync_to_async

from riddler.apps.broker.models.message import Message
from logging import getLogger

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
    ubiquitous: bool
        It describes a state that can be accessed from any other state, it is just a shortcut for not adding this state
        to all the rest ones in the transitions definition
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
    dest: str
        'to' state
    conditions: List of str
        A list of strings which are the function's names needed to be executed to determine if we can enter the 'dest'
        state
    unless: List of str
        The same as conditions but considering the function with a 'not' operator in front of it
    """
    source: Text
    dest: Text
    conditions: List[Text] = []
    unless: List[Text] = []


class MachineContext:
    """
    Abstract class all http views/WS representing a bot should inherit from,
    this way we have a generic and shared functionality across the different
    bots whatever what kind they are (WebSocket based, http views and what not)
    making the FSM states access to this 'connection' functionality
    """
    def __init__(self, *args, **kargs):
        self.conversation_id = None
        self.fsm_name = None
        super().__init__(*args, **kargs)

    async def send_response(self, *args, **kargs):
        raise NotImplementedError(
            "All classes that behave as contexts for machines should implement 'send_response'"
        )

    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id

    def set_fsm_name(self, fsm_name):
        self.fsm_name = fsm_name

    async def get_last_mml(
        self,
    ) -> Message:  # TODO: property return type for a coroutine
        return await sync_to_async(
            Message.objects.filter(conversation=self.conversation_id)
            .order_by("-created_date")
            .first
        )()


class Machine:
    def __init__(
        self,
        ctx: MachineContext,
        states: List[State],
        transitions: List[Transition],
        current_state: State = None,
    ):
        self.ctx = ctx
        self.states = states
        self.transitions = transitions

        self.current_state = current_state
        if not current_state:
            self.current_state = self.get_initial_state()

    async def start(self):
        await self.run_current_state_events()
        logger.debug(f"FSM start --> {self.current_state}")
        await self.save_cache()

    async def next_state(self):
        transitions = self.get_current_state_transitions()
        for t in transitions:
            if await self.check_transition_condition(t):
                logger.debug(f"FSM from ---> {self.current_state}")
                self.current_state = self.get_state_by_name(t.dest)
                logger.debug(f"FSM to -----> {self.current_state}")
                await self.run_current_state_events()
                break
        await self.save_cache()

    async def run_current_state_events(self):
        for event in self.current_state.events:
            await getattr(self.ctx, event)()

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
        return filter(lambda t: t.source == self.current_state.name, self.transitions)

    async def check_transition_condition(self, transition):
        for condition in transition.conditions:
            if not await getattr(self.ctx, condition)():
                return False

        for condition in transition.unless:
            if await getattr(self.ctx, condition)():
                return False

        return True

    async def save_cache(self):
        from riddler.apps.fsm.models import CachedMachine  # TODO: Resolve CI

        await sync_to_async(CachedMachine.update_or_create)(self)
