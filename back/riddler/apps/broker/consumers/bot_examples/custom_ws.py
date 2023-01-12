import asyncio

import json
from riddler.common.abs.bot_consumers.ws import WSBotConsumer
from logging import getLogger

from ...serializers.message import ExampleWSSerializer
from riddler.utils import WSStatusCodes

logger = getLogger(__name__)


class CustomWSBotConsumer(WSBotConsumer):
    """
    A very simple implementation of the AbsBotConsumer just to show how could a Riddler bot work
    """

    serializer_class = ExampleWSSerializer

    def gather_platform_config(self):
        from ...models.platform_config import PlatformConfig  # TODO: Fix CI
        pk = self.scope["url_route"]["kwargs"]["pc_id"]
        return PlatformConfig.objects.select_related("fsm_def").get(pk=pk)

    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]

    async def send_response(self, stacks: list):
        for stack in stacks:
            for layer in stack:
                if layer.get("type") == "text":
                    await self.channel_layer.group_send(
                        self.get_group_name(), {"type": "response", "status": WSStatusCodes.ok.value, "payload": layer["payload"]}
                    )
                else:
                    logger.warning(f"Layer not supported: {layer}")

    async def response(self, data: dict):
        print(f"NOW: {data}")
        await self.send(json.dumps(data))
