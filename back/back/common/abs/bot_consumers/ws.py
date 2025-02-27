import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from back.apps.fsm.models import CachedFSM
from back.common.abs.bot_consumers import BotConsumer
from back.utils import WSStatusCodes


logger = getLogger(__name__)


class WSBotConsumer(BotConsumer, AsyncJsonWebsocketConsumer):
    """
    Abstract class all views representing an WS bot should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """

    async def connect(self):
        await self.accept()
        fsm_def, error = await self.gather_fsm_def()
        if not fsm_def:  # FSM doesnt exist
            await self.close(4000, reason=error or "`Error retrieving FSM definition`")
            return
        self.set_fsm_def(fsm_def)
        self.set_user_id(await self.gather_user_id())

        await self.set_conversation(self.gather_conversation_id(), await self.gather_initial_conversation_metadata(), self.fsm_def.authentication_required, await self.gather_fsm_state_overwrite())
        if not await self.authenticate():
            await self.close(3000, reason="`Authentication failed`")

        self.fsm = await database_sync_to_async(CachedFSM.build_fsm)(self)
        # Join room group
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        if self.fsm:
            logger.debug(
                f"Continuing conversation ({self.conversation}), reusing cached conversation's FSM ({await database_sync_to_async(CachedFSM.get_conv_updated_date)(self)})"
            )

            if not await self.fsm.check_sdk_connection():
                await self.close(4000, reason=f"`No RPC worker {self.fsm_def.name} connected`")  # no SDK connected
                return

            # await self.fsm.next_state()
        else:
            self.fsm = await database_sync_to_async(self.fsm_def.build_fsm)(self, None)

            if not await self.fsm.check_sdk_connection():
                await self.close(4000, reason=f"`No RPC worker {self.fsm_def.name} connected`")  # no SDK connected
                return

            await self.fsm.start()
            logger.debug(
                f"Starting new WS conversation (channel group: {self.get_group_name()}) and creating new FSM"
            )

    async def receive_json(self, content, **kwargs):
        if content.get("heartbeat", False):
            for _shard in self.channel_layer._shards:
                try:
                    await _shard._redis.ping()
                except ConnectionError as e:
                    # Since the Redis connection error on DO happens in any call to redis, is very common it happens
                    # here, since this is trigger quite often, lets see if this try catch solves de reconnection
                    logger.error(f" --------------------- Error on ping: {e}")
            return
        if content.get("reset"):
            await self.fsm.reset(content["reset"])
            return

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

    async def send_response(self, data):
        for _res in self.serializer_class.to_platform(data, self):
            _res["type"] = "response"
            await self.channel_layer.group_send(self.get_group_name(), _res)

    async def response(self, data: dict):
        await self.send(json.dumps(data))
