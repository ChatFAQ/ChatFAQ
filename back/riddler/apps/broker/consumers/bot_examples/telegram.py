from logging import getLogger

from asgiref.sync import sync_to_async

from riddler.apps.broker.serializers.message import TelegramMessageSerializer
from riddler.apps.fsm.models import FSMDefinition
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer

logger = getLogger(__name__)


class TelegramBotConsumer(HTTPBotConsumer):
    serializer_class = TelegramMessageSerializer

    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]

    async def gather_platform_config(self, scope):
        from riddler.apps.broker.models.platform_config import PlatformConfig  # TODO: Fix CI
        token = scope["path"].split("/")[-1]
        return await sync_to_async(PlatformConfig.objects.get)(platform_meta__token=token)

    async def gather_fsm_def(self, validated_data):
        pk = self.platform_config.platform_meta["fsm_def_id"]
        return await sync_to_async(FSMDefinition.objects.get)(pk=pk)
