import requests
from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer

    def gather_platform_config(self, scope):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: Fix CI
        token = scope["path"].split("/")[-1]
        return PlatformConfig.objects.select_related("fsm_def").get(platform_meta__token=token)

    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]

    async def send_response(self, stacks: list):
        data = {
            "chat_id": self.conversation_id,
            "text": stacks[0][0]["payload"],
            "parse_mode": "Markdown",
        }
        requests.post(
            f"{self.platform_config.platform_meta['api_url']}{self.platform_config.platform_meta['token']}/sendMessage", data=data
        )
