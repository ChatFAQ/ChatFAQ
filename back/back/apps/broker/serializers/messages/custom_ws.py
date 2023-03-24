import time
from logging import getLogger
from typing import TYPE_CHECKING, Union

from asgiref.sync import async_to_sync
from rest_framework import serializers

from back.apps.broker.models.message import AgentType
from back.apps.broker.serializers.messages import (
    AgentSerializer,
    BotMessageSerializer,
    MessageSerializer,
    MessageStackSerializer,
)
from back.common.abs.bot_consumers import BotConsumer
from back.utils import WSStatusCodes

if TYPE_CHECKING:
    from back.apps.broker.models.message import Message

logger = getLogger(__name__)


class ExampleWSSerializer(BotMessageSerializer):
    stacks = serializers.ListField(
        child=serializers.ListField(child=MessageStackSerializer())
    )
    transmitter = AgentSerializer()

    def to_mml(self, ctx: BotConsumer) -> Union[bool, "Message"]:

        if not self.is_valid():
            return False

        s = MessageSerializer(
            data={
                "stacks": self.data["stacks"],
                "transmitter": self.data["transmitter"],
                "send_time": int(time.time() * 1000),
                "conversation": ctx.conversation_id,
            }
        )
        if not s.is_valid():
            return False
        return s.save()

    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer) -> dict:
        s = MessageSerializer(mml)
        yield s.data
