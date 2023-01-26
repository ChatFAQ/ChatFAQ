from asgiref.sync import sync_to_async

from riddler.apps.fsm.models import FSMDefinition
from riddler.common.abs.bot_consumers.ws import WSBotConsumer
from logging import getLogger

from riddler.apps.broker.serializers.messages.custom_ws import ExampleWSSerializer

logger = getLogger(__name__)


class CustomWSBotConsumer(WSBotConsumer):
    """
    A very simple implementation of the AbsBotConsumer just to show how could a Riddler bot work
    """

    serializer_class = ExampleWSSerializer

    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]

    async def gather_fsm_def(self):
        pk = self.scope["url_route"]["kwargs"]["fsm_def_id"]
        return await sync_to_async(FSMDefinition.objects.get)(pk=pk)

    @classmethod
    def platform_url_path(self) -> str:
        return r"back/ws/broker/(?P<conversation>\w+)/(?P<fsm_def_id>\w+)/$"

    @classmethod
    def register(cls):
        pass
