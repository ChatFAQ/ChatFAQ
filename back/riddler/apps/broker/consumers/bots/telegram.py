from logging import getLogger
from urllib.parse import urljoin

import httpx
import requests
from asgiref.sync import sync_to_async
from django.conf import settings

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.models import FSMDefinition
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer

logger = getLogger(__name__)


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer
    API_URL = "https://api.telegram.org/bot"
    TOKEN = settings.TG_TOKEN

    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]

    async def gather_fsm_def(self, validated_data):
        return await sync_to_async(FSMDefinition.objects.first)()

    async def send_response(self, mml: Message):
        async with httpx.AsyncClient() as client:
            for data in self.serializer_class.to_platform(mml, self):
                await client.post(
                    f"{self.API_URL}{self.TOKEN}/sendMessage", data=data
                )

    @classmethod
    def platform_url_path(self) -> str:
        return f"back/webhooks/broker/telegram/{self.TOKEN}"

    @classmethod
    def register(cls):
        webhookUrl = urljoin(settings.BASE_URL, cls.platform_url_path())
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
