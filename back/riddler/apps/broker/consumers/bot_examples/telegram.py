from logging import getLogger

import httpx

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer

logger = getLogger(__name__)


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer

    def gather_platform_config(self, scope):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: Fix CI
        token = scope["path"].split("/")[-1]
        return PlatformConfig.objects.select_related("fsm_def").get(platform_meta__token=token)

    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]

    async def send_response(self, mml: Message):
        async with httpx.AsyncClient() as client:
            for stack in mml.stacks:
                for layer in stack:
                    if layer.get("type") == "text":
                        data = {
                            "chat_id": self.conversation_id,
                            "text": layer["payload"],
                            "parse_mode": "Markdown",
                        }
                        await client.post(
                            f"{self.platform_config.platform_meta['api_url']}{self.platform_config.platform_meta['token']}/sendMessage", data=data
                        )
                    else:
                        logger.warning(f"Layer not supported: {layer}")

