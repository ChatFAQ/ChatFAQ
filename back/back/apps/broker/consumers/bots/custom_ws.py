import json
from logging import getLogger
from urllib.parse import parse_qs

from channels.db import database_sync_to_async

from back.apps.broker.serializers.messages.custom_ws import ExampleWSSerializer
from back.apps.fsm.models import FSMDefinition
from back.common.abs.bot_consumers.ws import WSBotConsumer

logger = getLogger(__name__)


class CustomWSBotConsumer(WSBotConsumer):
    """
    A very simple implementation of the AbsBotConsumer just to show how could a ChatFAQ bot work
    """

    serializer_class = ExampleWSSerializer

    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]

    async def gather_fsm_def(self):
        name = self.scope["url_route"]["kwargs"]["fsm_def"]
        fsm = await database_sync_to_async(FSMDefinition.objects.filter(name=name).first)()
        return fsm, None if fsm else f"No FSM found with name {name}"

    async def gather_user_id(self):
        return self.scope["url_route"]["kwargs"]["sender_id"]

    async def gather_initial_conversation_metadata(self):
        params = parse_qs(self.scope["query_string"])
        _meta = params.get(b"metadata", [b"{}"])
        return json.loads(_meta[0])

    @classmethod
    def platform_url_paths(cls) -> str:
        yield r"back/ws/broker/(?P<conversation>[\w-]+)/(?P<fsm_def>[\w-]+)/$"
        yield r"back/ws/broker/(?P<conversation>[\w-]+)/(?P<fsm_def>[\w-]+)/(?P<sender_id>[\w-]+)/$"

    @classmethod
    def register(cls):
        pass
