import asyncio
from logging import getLogger
from typing import TYPE_CHECKING, Union, Tuple

from channels.db import database_sync_to_async
from django.forms import model_to_dict
from django.urls import re_path

from back.apps.broker.models.message import Conversation, Message
from back.utils.custom_channels import CustomAsyncConsumer
from django.contrib.auth.models import AnonymousUser

if TYPE_CHECKING:
    from back.apps.fsm.lib import FSM
    from back.apps.fsm.models import FSMDefinition

logger = getLogger(__name__)


class BrokerMetaClass(type):
    registry = []

    def __new__(cls, cls_name, bases, attrs):
        new_class = super().__new__(cls, cls_name, bases, attrs)
        if (
            cls_name != "BotConsumer"
            and cls_name != "WSBotConsumer"
            and cls_name != "HTTPBotConsumer"
        ):
            cls.registry.append(new_class)
        return new_class


class BotConsumer(CustomAsyncConsumer, metaclass=BrokerMetaClass):
    """
    Abstract class all HTTP/WS consumers representing a bot should inherit from,
    this way we have a generic and shared functionality across the different
    bots whatever what kind they are (WebSocket based, http views and what not).
    The FSM, serializers and what not will probably access methods of this class to get information about the
    conversation, platform_config, etc...
    """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        from back.apps.broker.serializers.messages import (
            BotMessageSerializer,  # TODO: CI
        )

        self.conversation: Union[Conversation, None] = None
        self.user_id: Union[str, None] = None

        self.fsm_def: "FSMDefinition" = None
        self.message_buffer = []
        super().__init__(*args, **kwargs)
        if self.serializer_class is None or not issubclass(
            self.serializer_class, BotMessageSerializer
        ):
            raise Exception(
                "serializer_class should not be None on any BotConsumer and should implement "
                "BotMessageSerializer"
            )

        self.fsm: "FSM" = None

    @staticmethod
    def create_group_name(conversation_id):
        return f"bot_{conversation_id}"

    def get_group_name(self):
        if self.conversation:
            return self.create_group_name(self.conversation.pk)

    async def rpc_response(self, data: dict):
        """
        This method is called as a consumer layer from the RPCConsumer once the response of the RPC server comes, it
        receives the data and keeps the execution of the fsm that in the first place requested a RPC call
        Parameters
        ----------
        data dict:
            response from the RPC Server, it can be the result of an FSM's condition or of an event

        Returns
        -------
            None

        """
        await self.fsm.manage_rpc_response(data)

    def rpc_result_streaming_generator(self):
        self.fsm.rpc_result_future = asyncio.get_event_loop().create_future()

        first_stack_group_id = self.message_buffer[0]["stack_group_id"]
        last_index_diff_stack_group_id = 0
        for index, msg in enumerate(self.message_buffer):
            if msg["stack_group_id"] != first_stack_group_id:
                break
            last_index_diff_stack_group_id = index
        _message_buffer = self.message_buffer[: last_index_diff_stack_group_id + 1]
        self.message_buffer = self.message_buffer[last_index_diff_stack_group_id + 1:]
        _stack = []
        for msg in _message_buffer:
            _stack += msg["stack"]
        if not self.message_buffer:
            return _stack, _message_buffer[-1]["stack_group_id"], _message_buffer[-1]["last"]
        else:
            self.fsm.rpc_result_future.set_result(self.rpc_result_streaming_generator)
            return _stack, _message_buffer[-1]["stack_group_id"], _message_buffer[-1]["last"]

    async def disconnect(self, code=None):
        logger.debug(
            f"Disconnecting from conversation ({self.conversation.pk}) (CODE: {code})"
            if self.conversation
            else f"Disconnecting... no conversation present, probably either not authenticated, wrong FSM name or no RPC worker connected... (CODE: {code})"
        )
        if self.fsm:
            while self.fsm.waiting_for_rpc:
                await asyncio.sleep(1)
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)

    async def send_response(self, stack: list):
        raise NotImplementedError(
            "All classes that behave as contexts for machines should implement 'send_response'"
        )

    def gather_initial_conversation_metadata(self, mml: "Message"):
        raise NotImplemented(
            "Implement a method that creates/gathers the conversation covnersation metadata"
        )

    def gather_conversation_id(self, mml: "Message"):
        raise NotImplemented(
            "Implement a method that creates/gathers the conversation id"
        )

    async def gather_fsm_def(self, mml: "Message") -> Tuple["FSMDefinition", str]:
        raise NotImplemented("Implement a method that gathers the conversation id")

    async def gather_user_id(self, mml: "Message"):
        return None

    async def authenticate(self):
        if not self.conversation.authentication_required:
            return True
        return (
            self.scope.get("user")
            and not isinstance(self.scope["user"], AnonymousUser)
        )

    async def set_conversation(self, platform_conversation_id, initial_conversation_metadata, authentication_required):
        self.conversation, created = await Conversation.objects.aget_or_create(
            platform_conversation_id=platform_conversation_id
        )
        if created:
            self.conversation.initial_conversation_metadata = initial_conversation_metadata
            self.conversation.authentication_required = authentication_required
            await database_sync_to_async(self.conversation.save)()

    def set_fsm_def(self, fsm_def):
        self.fsm_def = fsm_def

    def set_user_id(self, user_id):
        self.user_id = user_id

    async def serialize(self):
        """
        We serialize the ctx just so we can send it to the RPC Servers
        """
        from back.apps.broker.models.message import Conversation  # TODO: CI
        from back.apps.fsm.models import FSMDefinition

        conv = await database_sync_to_async(Conversation.objects.get)(pk=self.conversation.pk)
        conv_mml = await database_sync_to_async(conv.get_conv_mml)()

        fsm_def = await database_sync_to_async(FSMDefinition.objects.get)(
            pk=self.fsm_def.pk
        )
        initial_state_values = fsm_def.initial_state_values
        initial_state_values = initial_state_values if initial_state_values else {}
        last_state_values = await database_sync_to_async(conv.get_last_state)()

        if last_state_values is None:
            last_state_values = initial_state_values
        else:
            # We keep the last state values and fill the missing ones with the initial state values
            for key, value in initial_state_values.items():
                if key not in last_state_values:
                    last_state_values[key] = value
        status = await database_sync_to_async(conv.get_last_status)()

        return {
            "conversation_id": self.conversation.pk,
            "initial_conversation_metadata": self.conversation.initial_conversation_metadata,
            "user_id": self.user_id,
            "conv_mml": conv_mml,
            "bot_channel_name": self.channel_name,
            "state": last_state_values,
            "status": status,
        }

    # ---------- Broker methods ----------
    @classmethod
    def platform_url_paths(cls) -> str:
        """
        For controlling the view's urls depending on the platform type since this name will
        most likely depend on the metadata of the platform
        """
        raise NotImplementedError

    @classmethod
    def build_path(cls):
        for platform_url_path in cls.platform_url_paths():
            yield re_path(platform_url_path, cls.as_asgi())

    @classmethod
    def register(cls):
        """
        In case we need to notify the remote message platform information as such our endpoint. This method will be
        executed for all platform configs when initializing the app
        """
        raise NotImplementedError
