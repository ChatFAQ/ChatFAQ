from logging import getLogger
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

