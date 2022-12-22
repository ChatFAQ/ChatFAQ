import requests

from ..models.message import Message
from ..serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.lib import FSMContext
from riddler.common.views import BotView
from riddler.config import settings


class TelegramBotView(BotView):
    serializer_class = TelegramMessageSerializer

    def gather_fsm_name(self, data):
        return "test"

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
            f"{settings.TG_BOT_API_URL}{settings.TG_TOKEN}/sendMessage", data=data
        )
