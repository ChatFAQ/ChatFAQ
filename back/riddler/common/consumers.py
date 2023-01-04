from abc import ABC
from logging import getLogger
from django.db import transaction

from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from riddler.apps.fsm.lib import FSM, FSMContext
from riddler.utils import WSStatusCodes

logger = getLogger(__name__)


class AbsBotConsumer(AsyncJsonWebsocketConsumer, FSMContext, ABC):
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

    def get_group_name(self):
        return f"bot_{self.conversation_id}"

    async def connect(self):
        self.set_conversation_id(self.gather_conversation_id())
        self.fsm = await self.initialize_fsm()
        logger.debug(
            f"Starting new WS conversation ({self.conversation_id}), creating new FSM"
        )

        # Join room group
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await self.accept()
        await self.fsm.start()

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

    async def receive_json(self, *args):
        serializer = self.serializer_class(data=args[0])
        if not await sync_to_async(serializer.is_valid)():
            await self.channel_layer.group_send(
                self.conversation_id, {"type": "response", "status": WSStatusCodes.bad_request.value, "payload": serializer.errors}
            )
        else:
            @transaction.atomic()
            def _aux(_serializer):
                _serializer.save()
                async_to_sync(self.fsm.next_state)()
            await sync_to_async(_aux)(serializer)

    async def response(self, data: dict):
        raise NotImplemented("'response' method should be implemented for all bot consumers")
