import asyncio

from abc import ABC
from logging import getLogger

from asgiref.sync import async_to_sync, sync_to_async
from django.db import transaction

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from riddler.apps.fsm.lib import FSM, FSMContext
from riddler.utils import WSStatusCodes
from riddler.utils.custom_channels import CustomAsyncConsumer

logger = getLogger(__name__)


class AbsBotConsumer(CustomAsyncConsumer, AsyncJsonWebsocketConsumer, FSMContext, ABC):
    """
    Abstract class all views representing an WS bot should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """
    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.serializer_class is None:
            raise Exception("serializer_class should not be None on any BotConsumer")

        self.fsm: FSM = None
        self.fsm_name: str = None

    @staticmethod
    def create_group_name(conversation_id):
        return f"bot_{conversation_id}"

    def get_group_name(self):
        return self.create_group_name(self.conversation_id)

    async def connect(self):
        self.set_conversation_id(self.gather_conversation_id())
        self.fsm = await self.initialize_fsm()
        # Join room group
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await self.accept()
        await self.fsm.start()
        logger.debug(
            f"Starting new WS conversation (channel group: {self.get_group_name()}) and creating new FSM"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from WS conversation ({self.conversation_id})")
        # Leave room group
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)

    async def initialize_fsm(self):
        logger.debug(f"Creating new FSM ({self.fsm_name})")
        pc = await sync_to_async(self.gather_platform_config)()
        self.set_platform_config(pc)
        # TODO: Support cached FSM ???
        return self.platform_config.fsm_def.build_fsm(self)

    async def receive_json(self, content, **kwargs):
        serializer = self.serializer_class(data=content)
        if not await sync_to_async(serializer.is_valid)():
            await self.channel_layer.group_send(
                self.get_group_name(), {"type": "response", "status": WSStatusCodes.bad_request.value, "payload": serializer.errors}
            )
        else:
            # It seems like django does not support transactions on async code
            # The commented code seems right but it is not: it blocks the save() methods inside from the RPCResponseConsumer
            # @transaction.atomic()
            # def _aux(_serializer):
            #     _serializer.save()
            #     async_to_sync(self.fsm.next_state)()
            # await sync_to_async(_aux)(serializer)

            await sync_to_async(serializer.save)()
            await self.fsm.next_state()

    async def rpc_response(self, data: dict):
        self.fsm.rpc_result_future.set_result(data["payload"])

    async def response(self, data: dict):
        raise NotImplemented("'response' method should be implemented for all bot consumers")
