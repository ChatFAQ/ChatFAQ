import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.http import AsyncHttpConsumer

from back.apps.broker.models.message import Message
from back.apps.fsm.models import CachedFSM
from back.common.abs.bot_consumers import BotConsumer

logger = getLogger(__name__)


class HTTPBotConsumer(BotConsumer, AsyncHttpConsumer):
    """
    Abstract class all HTTP bot consumers should inherit from,
    it takes care of the initialization and management of the fsm and
    the persistence of the sending/receiving MMLs into the database
    """

    async def resolve_fsm(self):
        """
        It will try to get a cached FSM from a provided name or create a new one in case
        there is no one yet (when is a brand-new conversation_id)

        Returns
        -------
        bool
            Whether or not it was able to create (new) or retrieve (cached) a FSM.
            If returns False most likely it is going be because a wrongly provided FSM name
        """

        self.fsm = await database_sync_to_async(CachedFSM.build_fsm)(self)
        if self.fsm:
            logger.debug(
                f"Continuing conversation ({self.conversation}), reusing cached conversation's FSM ({await database_sync_to_async(CachedFSM.get_conv_updated_date)(self)})"
            )
            await self.fsm.next_state()
        else:
            logger.debug(
                f"Starting new conversation ({self.conversation}), creating new FSM"
            )
            self.fsm = self.fsm_def.build_fsm(self)
            await self.fsm.start()

        return True

    async def handle(self, body):
        """
        Entry point for the message coming from the platform, here we will serialize such message,
        store it in the database and call the FSM
        """

        data = await self._check_valid_json(body)
        if data is None:
            return

        await self.send_headers(
            headers=[
                (b"Content-Type", b"application/json"),
            ]
        )
        serializer = self.serializer_class(data=data)
        serializer.is_valid()

        await self.set_conversation(
            self.gather_conversation_id(serializer.validated_data)
        )
        self.set_fsm_def(await self.gather_fsm_def(serializer.validated_data))
        self.set_user_id(await self.gather_user_id(serializer.validated_data))

        mml = await database_sync_to_async(serializer.to_mml)(self)
        if not mml:
            await self.send_json(serializer.errors)
            return

        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)

        await self.resolve_fsm()
        await self.send_json({"ok": "POST request processed"})

    async def send_json(self, data, more_body=False):
        await self.send_body(json.dumps(data).encode("utf-8"), more_body=more_body)

    async def _check_valid_json(self, body):
        try:
            data = json.loads(body.decode("utf-8"))
        except json.decoder.JSONDecodeError as e:
            logger.error(e)
            await self.send_json({"error": "Wrong JSON"})
            return
        return data

    async def send_response(self, mml: Message):
        raise NotImplementedError
