import json

import asyncio

import requests
from channels.generic.http import AsyncHttpConsumer

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.lib import FSMContext
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer

    def gather_platform_config(self, scope):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: Fix CI
        token = scope["path"].split("/")[-1]
        return PlatformConfig.objects.select_related("fsm_def").get(platform_meta__token=token)

    def gather_conversation_id(self, mml: Message):
        return mml.conversation

    @staticmethod
    async def send_response(ctx: FSMContext, msg: str):
        data = {
            "chat_id": ctx.conversation_id,
            "text": msg,
            "parse_mode": "Markdown",
        }
        requests.post(
            f"{ctx.platform_config.platform_meta['api_url']}{ctx.platform_config.platform_meta['token']}/sendMessage", data=data
        )
