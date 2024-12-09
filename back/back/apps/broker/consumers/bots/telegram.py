from logging import getLogger
from urllib.parse import urljoin

import httpx
import requests

from channels.db import database_sync_to_async
from django.conf import settings

from back.apps.broker.models.message import Message
from back.apps.broker.serializers.messages.telegram import TelegramMessageSerializer
from back.apps.fsm.models import FSMDefinition
from back.common.abs.bot_consumers.http import HTTPBotConsumer

logger = getLogger(__name__)


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer
    API_URL = "https://api.telegram.org/bot"
    TOKEN = settings.TG_TOKEN

    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]

    async def gather_fsm_def(self, validated_data):
        fsm = await database_sync_to_async(FSMDefinition.objects.first)()
        return fsm, None if fsm else f"No FSM found"

    @classmethod
    def platform_url_paths(self) -> str:
        yield f"back/webhooks/broker/telegram/{self.TOKEN}"

    @classmethod
    def register(cls):
        if not cls.TOKEN:
            return

        for platform_url_path in cls.platform_url_paths():
            webhookUrl = urljoin(settings.BASE_URL, platform_url_path)
            logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
            res = requests.get(
                f"{cls.API_URL}{cls.TOKEN}/setWebhook",
                params={"url": webhookUrl},
            )
            if res.ok:
                logger.debug(
                    f"Successfully notified  WebhookUrl ({webhookUrl}) to Telegram"
                )
            else:
                logger.error(
                    f"Error notifying  WebhookUrl ({webhookUrl}) to Telegram: {res.text}"
                )

    async def send_response(self, mml: Message):
        async with httpx.AsyncClient() as client:
            for data in self.serializer_class.to_platform(mml, self):
                await client.post(f"{self.API_URL}{self.TOKEN}/sendMessage", data=data)
