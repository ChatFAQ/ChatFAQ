from abc import ABC
from logging import getLogger
from typing import Union

from asgiref.sync import sync_to_async
from django.forms import model_to_dict

from riddler.apps.broker.models.message import Message
from riddler.utils.custom_channels import CustomAsyncConsumer
from rest_framework.request import Request

logger = getLogger(__name__)


class BotConsumer(CustomAsyncConsumer, ABC):
    """
    Abstract class all HTTP/WS consumers representing a bot should inherit from,
    this way we have a generic and shared functionality across the different
    bots whatever what kind they are (WebSocket based, http views and what not).
    The FSM, serializers and what not will probably access methods of this class to get information about the
    conversation_id, platform_config, etc...
    """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: CI
        from riddler.apps.broker.serializers.message import BotMessageSerializer  # TODO: CI
        from riddler.apps.fsm.models import FSMDefinition  # TODO: CI
        from riddler.apps.fsm.lib import FSM  # TODO: CI

        self.conversation_id: Union[str, None] = None
        self.fsm_def: FSMDefinition = None
        self.platform_config: Union[PlatformConfig, None] = None

        super().__init__(*args, **kwargs)
        if self.serializer_class is None or not issubclass(self.serializer_class, BotMessageSerializer):
            raise Exception("serializer_class should not be None on any BotConsumer and should implement "
                            "ToMMLSerializer methods")

        self.fsm: FSM = None

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

    def gather_conversation_id(self, mml: Message = None):
        raise NotImplemented("Implement a method that gathers the conversation id")

    async def gather_fsm_def(self, mml: Message = None):
        raise NotImplemented("Implement a method that gathers the conversation id")

    async def gather_platform_config(self, request: Request = None):
        raise NotImplemented("Implement a method that gathers the fsm name")

    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id

    def set_fsm_def(self, fsm_def):
        self.fsm_def = fsm_def

    def set_platform_config(self, platform_config):
        self.platform_config = platform_config

    async def get_last_mml(
        self,
    ) -> Message:
        """
        Utility function just to gather the last message on the conversation, it is ofter useful to know what to respond to!

        Returns
        -------
        Message
            Last message from the conversation

        """
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
