import requests

from ..models.message import Message
from ..models.platform_config import PlatformConfig
from ..serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.lib import FSMContext
from riddler.common.views import AbsBotView
from riddler.config import settings


class TelegramBotView(AbsBotView):
    serializer_class = TelegramMessageSerializer

    def gather_platform_config(self, request):
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
