import requests
from rest_framework.response import Response

from api.broker.serializers import TelegramMessageSerializer
from api.common.views import BotView
from api.fsm.lib import MachineContext
from config import settings


class TelegramBotView(BotView):
    serializer_class = TelegramMessageSerializer

    def get_fsm_name(self, data):
        return "test"

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)
    #     return Response({"ok": "POST request processed"})

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
