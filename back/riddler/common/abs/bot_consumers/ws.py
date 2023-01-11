from logging import getLogger

from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from riddler.common.abs.bot_consumers import BotConsumer
from riddler.utils import WSStatusCodes

logger = getLogger(__name__)


class WSBotConsumer(BotConsumer, AsyncJsonWebsocketConsumer):
    """
    Abstract class all views representing an WS bot should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """
    async def connect(self):
        self.set_conversation_id(self.gather_conversation_id())
        pc = await sync_to_async(self.gather_platform_config)()
        self.set_platform_config(pc)

        # TODO: Support cached FSM ???
        self.fsm = self.platform_config.fsm_def.build_fsm(self)

        # Join room group
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await self.accept()
        await self.fsm.start()
        logger.debug(
            f"Starting new WS conversation (channel group: {self.get_group_name()}) and creating new FSM"
        )

    async def receive_json(self, content, **kwargs):
        serializer = self.serializer_class(data=content)
        mml = await sync_to_async(serializer.to_mml)(self)
        if not mml:
            await self.channel_layer.group_send(
                self.get_group_name(), {"type": "response", "status": WSStatusCodes.bad_request.value, "payload": serializer.errors}
            )
            return

        # It seems like django does not support transactions on async code
        # The commented code seems right but it is not: it blocks the save() methods inside from the RPCResponseConsumer
        # @transaction.atomic()
        # def _aux(_serializer):
        #     _serializer.save()
        #     async_to_sync(self.fsm.next_state)()
        # await sync_to_async(_aux)(serializer)

        await self.fsm.next_state()
