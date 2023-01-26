import time

from asgiref.sync import async_to_sync
from typing import Union
from riddler.apps.broker.models.message import AgentType

from rest_framework import serializers

from riddler.apps.broker.serializers.messages import BotMessageSerializer, MessageStackSerializer, MessageSerializer
from riddler.common.abs.bot_consumers import BotConsumer


from logging import getLogger

from riddler.utils import WSStatusCodes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from riddler.apps.broker.models.message import Message

logger = getLogger(__name__)


class ExampleWSSerializer(BotMessageSerializer):
    stacks = serializers.ListField(child=serializers.ListField(child=MessageStackSerializer()))

    def to_mml(self, ctx: BotConsumer) -> Union[bool, "Message"]:

        if not self.is_valid():
            return False

        last_mml = async_to_sync(ctx.get_last_mml)()
        s = MessageSerializer(
            data={
                "stacks": self.data["stacks"],
                "transmitter": {
                    "type": AgentType.human.value,
                    "platform": "WS",
                },
                "send_time": int(time.time() * 1000),
                "conversation": ctx.conversation_id,
                "prev": last_mml.pk if last_mml else None
            }
        )
        if not s.is_valid():
            return False
        return s.save()

    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer) -> dict:
        for stack in mml.stacks:
            for layer in stack:
                if layer.get("type") == "text":
                    data = {
                        "status": WSStatusCodes.ok.value,
                        "payload": layer["payload"]
                    }
                    yield data
                else:
                    logger.warning(f"Layer not supported: {layer}")
