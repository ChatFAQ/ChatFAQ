import json
from logging import getLogger
from typing import TYPE_CHECKING

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from back.apps.fsm.models import CachedFSM
from back.common.abs.bot_consumers import BotConsumer
from back.utils import WSStatusCodes

if TYPE_CHECKING:
    from back.apps.broker.models.message import Message


logger = getLogger(__name__)


class WSBotConsumer(BotConsumer, AsyncJsonWebsocketConsumer):
    """
    Abstract class all views representing an WS bot should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """

    async def connect(self):
        await self.set_conversation(self.gather_conversation_id())
        self.set_fsm_def(await self.gather_fsm_def())
        self.set_user_id(await self.gather_user_id())

        # TODO: Support cached FSM ???
        self.fsm = await database_sync_to_async(CachedFSM.build_fsm)(self)
        # Join room group
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await self.accept()
        if self.fsm:
            logger.debug(
                f"Continuing conversation ({self.conversation}), reusing cached conversation's FSM ({await database_sync_to_async(CachedFSM.get_conv_updated_date)(self)})"
            )
            # await self.fsm.next_state()
        else:
            self.fsm = self.fsm_def.build_fsm(self)
            await self.fsm.start()
            logger.debug(
                f"Starting new WS conversation (channel group: {self.get_group_name()}) and creating new FSM"
            )

    async def receive_json(self, content, **kwargs):
        serializer = self.serializer_class(data=content)
        mml = await database_sync_to_async(serializer.to_mml)(self)
        if not mml:
            await self.channel_layer.group_send(
                self.get_group_name(),
                {
                    "type": "response",
                    "status": WSStatusCodes.bad_request.value,
                    "payload": serializer.errors,
                },
            )
            return
        """
        if not self.fsm.rpc_result_future.done():
            # TODO: Is this possible on the http consumer?
            await self.channel_layer.group_send(
                self.get_group_name(),
                {
                    "type": "response",
                    "status": WSStatusCodes.bad_request.value,
                    "payload": "Wait for the previous menssage to be processed",
                },
            )
            return
        """
        # It seems like django does not support transactions on async code
        # The commented code seems right but it is not: it blocks the save()
        # methods inside from the RPCResponseConsumer
        # @transaction.atomic()
        # def _aux(_serializer):
        #     _serializer.save()
        #     async_to_sync(self.fsm.next_state)()
        # await database_sync_to_async(_aux)(serializer)

        await self.fsm.next_state()

    async def send_response(self, mml: "Message"):
        for data in self.serializer_class.to_platform(mml, self):
            data["type"] = "response"
            await self.channel_layer.group_send(self.get_group_name(), data)

    async def response(self, data: dict):
        await self.send(json.dumps(data))
