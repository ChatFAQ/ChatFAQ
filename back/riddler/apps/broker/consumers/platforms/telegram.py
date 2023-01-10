import requests

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.lib import FSMContext
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer

    def gather_platform_config(self, request):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: Fix CI
        token = request.stream.path.split("/")[-1]
        return PlatformConfig.objects.get(platform_meta__token=token)

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
