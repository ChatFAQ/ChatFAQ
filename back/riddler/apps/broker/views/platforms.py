import requests
from rest_framework.response import Response

from riddler.apps.broker.models.message import Message
from riddler.apps.broker.serializers import TelegramMessageSerializer
from riddler.apps.fsm.lib import MachineContext
from riddler.common.views import BotView
from riddler.config import settings


class TelegramBotView(BotView):
    serializer_class = TelegramMessageSerializer

    def gather_fsm_name(self, data):
        return "test"

    def gather_conversation_id(self, mml: Message):
        return mml.conversation

    @staticmethod
    async def send_response(ctx: MachineContext, msg: str):
        data = {
            "chat_id": ctx.conversation_id,
            "text": msg,
            "parse_mode": "Markdown",
        }
        requests.post(
            f"{settings.TG_BOT_API_URL}{settings.TG_TOKEN}/sendMessage", data=data
        )
