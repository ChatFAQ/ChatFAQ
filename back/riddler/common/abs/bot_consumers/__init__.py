from abc import ABC
from logging import getLogger
from typing import Union

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from django.urls import re_path

from riddler.utils.custom_channels import CustomAsyncConsumer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from riddler.apps.fsm.models import FSMDefinition
    from riddler.apps.fsm.lib import FSM
    from riddler.apps.broker.models.message import Message

logger = getLogger(__name__)


class BrokerMetaClass(type):
    registry = []

    def __new__(cls, cls_name, bases, attrs):
        new_class = super().__new__(cls, cls_name, bases, attrs)
        if cls_name != "BotConsumer" and cls_name != "WSBotConsumer" and cls_name != "HTTPBotConsumer":
            cls.registry.append(new_class)
        return new_class


class BotConsumer(CustomAsyncConsumer, metaclass=BrokerMetaClass):
    """
    Abstract class all HTTP/WS consumers representing a bot should inherit from,
    this way we have a generic and shared functionality across the different
    bots whatever what kind they are (WebSocket based, http views and what not).
    The FSM, serializers and what not will probably access methods of this class to get information about the
    conversation_id, platform_config, etc...
    """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        from riddler.apps.broker.serializers.message import BotMessageSerializer  # TODO: CI

        self.conversation_id: Union[str, None] = None
        self.fsm_def: "FSMDefinition" = None

        super().__init__(*args, **kwargs)
        if self.serializer_class is None or not issubclass(self.serializer_class, BotMessageSerializer):
            raise Exception("serializer_class should not be None on any BotConsumer and should implement "
                            "BotMessageSerializer")

        self.fsm: "FSM" = None

    @staticmethod
    def create_group_name(conversation_id):
        return f"bot_{conversation_id}"

    def get_group_name(self):
        return self.create_group_name(self.conversation_id)

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
        self.fsm.rpc_result_future.set_result(data["payload"])

    async def disconnect(self, code=None):
        logger.debug(f"Disconnecting from conversation ({self.conversation_id}) (CODE: {code})")
        # Leave room group
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)

    async def send_response(self, stacks: list):
        raise NotImplementedError(
            "All classes that behave as contexts for machines should implement 'send_response'"
        )

    def gather_conversation_id(self, mml: "Message"):
        raise NotImplemented("Implement a method that gathers the conversation id")

    async def gather_fsm_def(self, mml: "Message"):
        raise NotImplemented("Implement a method that gathers the conversation id")

    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id

    def set_fsm_def(self, fsm_def):
        self.fsm_def = fsm_def

    async def get_last_mml(
        self,
    ):

        """
        Utility function just to gather the last message on the conversation, it is ofter useful to know what to respond to!

        Returns
        -------
        Message
            Last message from the conversation

        """
        from riddler.apps.broker.models.message import Message  # TODO: CI

        return await sync_to_async(
            Message.objects.filter(conversation=self.conversation_id)
            .order_by("-created_date")
            .first
        )()

    async def serialize(self):
        """
        We serialize the ctx just so we can send it to the RPC Servers
        """
        last_mml = await self.get_last_mml()
        last_mml = model_to_dict(last_mml, fields=["stacks"]) if last_mml else None
        return {
            "conversation_id": self.conversation_id,
            "last_mml": last_mml,
        }

    # ---------- Broker methods ----------
    @classmethod
    def platform_url_path(cls) -> str:
        """
        For controlling the view's url depending on the platform type since this name will
        most likely depend on the metadata of the platform
        """
        raise NotImplementedError

    @classmethod
    def build_path(cls):
        return re_path(
            cls.platform_url_path(),
            cls.as_asgi()
        )

    @classmethod
    def register(cls):
        """
        In case we need to notify the remote message platform information as such our endpoint. This method will be
        executed for all platform configs when initializing the app
        """
        raise NotImplementedError
