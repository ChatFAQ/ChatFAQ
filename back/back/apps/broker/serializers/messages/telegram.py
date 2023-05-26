from logging import getLogger
from typing import TYPE_CHECKING, Union

from asgiref.sync import async_to_sync
from rest_framework import serializers

from back.apps.broker.models.message import AgentType
from back.apps.broker.serializers.messages import (
    BotMessageSerializer,
    MessageSerializer,
)
from back.common.abs.bot_consumers import BotConsumer

if TYPE_CHECKING:
    from back.apps.broker.models.message import Message

logger = getLogger(__name__)


class TelegramFromSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_bot = serializers.BooleanField()
    first_name = serializers.CharField()
    language_code = serializers.CharField(max_length=2, min_length=2)


class TelegramChatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    type = serializers.CharField()


class TelegramPayloadSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    _from = TelegramFromSerializer()
    chat = TelegramChatSerializer()
    date = serializers.IntegerField()
    text = serializers.CharField()


# Hack to allow reserve word 'from' as serializer field
TelegramPayloadSerializer._declared_fields[
    "from"
] = TelegramPayloadSerializer._declared_fields["_from"]
del TelegramPayloadSerializer._declared_fields["_from"]


class TelegramMessageSerializer(BotMessageSerializer):
    message = TelegramPayloadSerializer()

    def to_mml(self, ctx: BotConsumer) -> Union[bool, "Message"]:

        if not self.is_valid():
            return False
        s = MessageSerializer(
            data={
                "stacks": [
                    [
                        {
                            "type": "text",
                            "payload": self.validated_data["message"]["text"],
                        }
                    ]
                ],
                "sender": {
                    "first_name": self.validated_data["message"]["from"]["first_name"],
                    "type": AgentType.human.value,
                    "platform": "Telegram",
                },
                "send_time": self.validated_data["message"]["date"] * 1000,
                "conversation": ctx.conversation.pk,
            }
        )
        if not s.is_valid():
            return False
        return s.save()

    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer):
        for stack in mml.stacks:
            for layer in stack:
                if layer.get("type") == "text":
                    data = {
                        "chat_id": ctx.conversation.platform_conversation_id,
                        "text": layer["payload"],
                        "parse_mode": "Markdown",
                    }
                    yield data
                else:
                    logger.warning(f"Layer not supported: {layer}")
