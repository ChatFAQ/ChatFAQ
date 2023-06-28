import asyncio
import copy
from abc import ABC
from logging import getLogger
from typing import TYPE_CHECKING, Union

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from django.urls import re_path

from back.apps.broker.consumers.message_types import RPCNodeType
from back.apps.broker.models.message import Conversation, Message
from back.utils.custom_channels import CustomAsyncConsumer

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
        if data["node_type"] == RPCNodeType.action.value:
            self.message_buffer.append(data)
            self.fsm.rpc_result_future.set_result(self.rpc_result_streaming_generator)
        else:
            self.fsm.rpc_result_future.set_result(data["stack"])

    def rpc_result_streaming_generator(self):
        self.fsm.rpc_result_future = asyncio.get_event_loop().create_future()

        first_stack_id = self.message_buffer[0]["stack_id"]
        last_index_diff_stack_id = 0
        for index, msg in enumerate(self.message_buffer):
            if msg["stack_id"] != first_stack_id:
                break
            last_index_diff_stack_id = index
        _message_buffer = self.message_buffer[: last_index_diff_stack_id + 1]
        self.message_buffer = self.message_buffer[last_index_diff_stack_id + 1:]
        _stack = []
        for msg in _message_buffer:
            _stack += msg["stack"]
        if not self.message_buffer:
            return _stack, _message_buffer[-1]["stack_id"], _message_buffer[-1]["last"]
        else:
            self.fsm.rpc_result_future.set_result(self.rpc_result_streaming_generator)
            return _stack, _message_buffer[-1]["stack_id"], _message_buffer[-1]["last"]

    async def disconnect(self, code=None):
        logger.debug(
            f"Disconnecting from conversation ({self.conversation.pk}) (CODE: {code})"
        )
        # Leave room group
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)

    async def send_response(self, stack: list):
        raise NotImplementedError(
            "All classes that behave as contexts for machines should implement 'send_response'"
        )

    def gather_conversation_id(self, mml: "Message"):
        raise NotImplemented(
            "Implement a method that creates/gathers the conversation id"
        )

    async def gather_fsm_def(self, mml: "Message"):
        raise NotImplemented("Implement a method that gathers the conversation id")

    async def gather_user_id(self, mml: "Message"):
        return None

    async def set_conversation(self, platform_conversation_id):
        self.conversation, _ = await Conversation.objects.aget_or_create(
            platform_conversation_id=platform_conversation_id
        )

    def set_fsm_def(self, fsm_def):
        self.fsm_def = fsm_def

    def set_user_id(self, user_id):
        self.user_id = user_id

    async def serialize(self):
        """
        We serialize the ctx just so we can send it to the RPC Servers
        """
        from back.apps.broker.models.message import Conversation  # TODO: CI

        conv = await sync_to_async(Conversation.objects.get)(pk=self.conversation.pk)
        last_mml = await sync_to_async(conv.get_last_mml)()

        last_mml = model_to_dict(last_mml, fields=["stack"]) if last_mml else None
        return {
            "conversation_id": self.conversation.pk,
            "last_mml": last_mml,
            "bot_channel_name": self.channel_name,
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
