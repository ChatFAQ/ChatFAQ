import time

from asgiref.sync import async_to_sync
from typing import Union
from riddler.apps.broker.models.message import StackPayloadType, AgentType

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from riddler.common.abs.bot_consumers import BotConsumer
from riddler.common.serializer_fields import JSTimestampField
from riddler.common.validators import AtLeastNOf, PresentTogether


from logging import getLogger

from riddler.utils import WSStatusCodes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from riddler.apps.broker.models.message import Message

logger = getLogger(__name__)


class BotMessageSerializer(serializers.Serializer):
    def to_mml(self, ctx: BotConsumer) -> "Message":
        """
        It should convert the validated data (it's called after calling 'is_valid') coming from the platform to a MML
        structure.

        Parameters
        ----------
        ctx: BotConsumer
            current context of the consumer using this serializer, useful for accessing the conversation_id, platform_config, etc


        Returns
        -------
        Message
            Saved MML

        """
        raise NotImplementedError(
            "You should implement a 'to_mml' method that converts your platform into an MML internal message"
        )

    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer) -> dict:
        """
        It should convert a MML coming from the FSM to the platform expected schema
        structure.

        Parameters
        ----------
        mml: Message
            FMS's message
        ctx: BotConsumer
            current context of the consumer using this serializer, useful for accessing the conversation_id, platform_config, etc

        Returns
        -------
        dict
            Payload to be sent to the platform

        """
        raise NotImplementedError(
            "You should implement a 'to_mml' method that converts your platform into an MML internal message"
        )


class AgentSerializer(serializers.Serializer):

    first_name = serializers.CharField(required=False, max_length=255)
    last_name = serializers.CharField(required=False, max_length=255)
    type = serializers.ChoiceField(choices=[n.value for n in AgentType])
    platform = serializers.CharField(required=False, max_length=255)

    class Meta:

        validators = [
            PresentTogether(fields=[{"type": AgentType.human.value}, "platform"])
        ]


class QuickReplySerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    id = serializers.CharField(max_length=255)
    meta = serializers.JSONField(required=False)


class Payload(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class MessageStackSerializer(serializers.Serializer):
    # TODO: Implement the corresponding validations over the 'payload' depending on the 'type'

    type = serializers.ChoiceField(
        choices=[n.value for n in StackPayloadType]
    )
    payload = Payload(required=False, allow_null=True)
    id = serializers.CharField(required=False, max_length=255)
    meta = serializers.JSONField(required=False)

    """
    satisfaction = serializers.ChoiceField(
        required=False, choices=[n.value for n in Satisfaction], allow_null=True
    )
    text = serializers.CharField(required=False)
    html = serializers.CharField(required=False)
    image = serializers.CharField(required=False)
    response_id = serializers.CharField(required=False)
    satisfaction = serializers.ChoiceField(
        required=False, choices=[n.value for n in Satisfaction], allow_null=True
    )
    meta = serializers.JSONField(required=False)
    quick_replies = QuickReplySerializer(required=False, many=True)
    """

    """
    class Meta:
        validators = [
            AtLeastNOf(
                fields=["text", "html", "image", "satisfaction", "quick_replies"],
                number=1,
            ),
            PresentTogether(fields=["response_id", "text"]),
        ]
    """


class MessageSerializer(serializers.ModelSerializer):
    stacks = serializers.ListField(child=serializers.ListField(child=MessageStackSerializer()))
    transmitter = AgentSerializer()
    receiver = AgentSerializer(required=False)
    send_time = JSTimestampField()

    class Meta:
        from riddler.apps.broker.models.message import Message  # TODO: CI
        model = Message
        fields = "__all__"

    def validate_prev(self, prev):
        """
        - There should be only one message with prev set to None
        - Prev should be None or belonging to the same conversation
        """
        from riddler.apps.broker.models.message import Message  # TODO: CI
        # It seems we are implementing "UniqueValidator" but nor really, because this will also fail for when value=None
        # and another message also already have value=None while UniqueValidator will not fail on this specific use case
        if Message.objects.filter(conversation=self.initial_data["conversation"], prev=prev).first():
            raise ValidationError(f"prev should be always unique for the same conversation")
        if prev and prev.conversation != str(self.initial_data["conversation"]):
            raise ValidationError(f"prev should belong to the same conversation")


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
        last_mml = async_to_sync(ctx.get_last_mml)()
        s = MessageSerializer(
            data={
                "stacks": [[{"type": "text", "payload": self.validated_data["message"]["text"]}]],
                "transmitter": {
                    "first_name": self.validated_data["message"]["from"]["first_name"],
                    "type": AgentType.human.value,
                    "platform": "Telegram",
                },
                "send_time": self.validated_data["message"]["date"] * 1000,
                "conversation": self.validated_data["message"]["chat"]["id"],
                "prev": last_mml.pk if last_mml else None
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
                        "chat_id": ctx.conversation_id,
                        "text": layer["payload"],
                        "parse_mode": "Markdown",
                    }
                    yield data
                else:
                    logger.warning(f"Layer not supported: {layer}")
