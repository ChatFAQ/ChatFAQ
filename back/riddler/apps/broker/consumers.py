import json
import time

from asgiref.sync import sync_to_async

from riddler.apps.fsm.lib import MachineContext
from riddler.common.consumers import BotConsumer

from .models import AgentType
from .serializers import MessageSerializer


class RiddlerConsumer(BotConsumer):
    def gather_fsm_name(self):
        return self.scope["url_route"]["kwargs"]["fsm"]

    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]

    async def send_response(self, ctx: MachineContext, msg: str):
        await self.channel_layer.group_send(
            ctx.conversation_id, {"type": "response", "text": msg}
        )

    async def response(self, data: dict):
        last_mml = await self.get_last_mml()
        serializer = MessageSerializer(
            data={
                "transmitter": {
                    "type": AgentType.bot.value,
                },
                "confidence": 1,
                "stacks": [[{
                    "type": "text",
                    "payload": data["text"],
                }]],
                "conversation": self.conversation_id,
                "send_time": int(time.time() * 1000),
                "prev": last_mml.pk if last_mml else None,
            }
        )
        await sync_to_async(serializer.is_valid)()
        await sync_to_async(serializer.save)()
        # Send message to WebSocket
        await self.send(json.dumps(serializer.data))
