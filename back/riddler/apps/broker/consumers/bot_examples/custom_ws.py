from asgiref.sync import sync_to_async

from riddler.apps.fsm.models import FSMDefinition
from riddler.common.abs.bot_consumers.ws import WSBotConsumer
from logging import getLogger

from ...serializers.message import ExampleWSSerializer

logger = getLogger(__name__)


class CustomWSBotConsumer(WSBotConsumer):
    """
    A very simple implementation of the AbsBotConsumer just to show how could a Riddler bot work
    """

    serializer_class = ExampleWSSerializer

    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]

    async def gather_platform_config(self):
        from ...models.platform_config import PlatformConfig  # TODO: Fix CI
        pk = self.scope["url_route"]["kwargs"]["pc_id"]
        return await sync_to_async(PlatformConfig.objects.get)(pk=pk)

    async def gather_fsm_def(self):
        pk = self.scope["url_route"]["kwargs"]["fsm_def_id"]
        return await sync_to_async(FSMDefinition.objects.get)(pk=pk)
