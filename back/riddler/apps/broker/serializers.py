from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# from ..common.consumers import BoilerplateConsumer # TODO resolve CI
from riddler.common.serializer_fields import JSTimestampField
from riddler.common.validators import AtLeastNOf, PresentTogether

from .models import AgentType, Message, StackPayloadType


class ToMMLSerializer(serializers.Serializer):
    def to_mml(self):
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
        model = Message
        fields = "__all__"

    def validate_prev(self, prev):
        """
        - There should be only one message with prev set to None
        - Prev should be None or belonging to the same conversation
        """
        # It seems we are implementing "UniqueValidator" but nor really, because this will also fail for when value=None
        # and another message also already have value=None while UniqueValidator will not fail on this specific use case
        if Message.objects.filter(prev=prev).first():
            raise ValidationError(f"prev should be always unique")
        if prev and prev.conversation != self.initial_data["conversation"]:
            raise ValidationError(f"prev should belong to the same conversation")


class BasicMessageSerializer(MessageSerializer, ToMMLSerializer):
    def to_mml(self):
        s = MessageSerializer(data=self.validated_data)
        s.is_valid(raise_exception=True)
        return s.save()


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


class TelegramMessageSerializer(ToMMLSerializer):
    message = TelegramPayloadSerializer()

    def to_mml(self) -> Message:
        s = MessageSerializer(
            data={
                "payload": {"text": self.validated_data["message"]["text"]},
                "transmitter": {
                    "first_name": self.validated_data["message"]["from"]["first_name"],
                    "type": AgentType.human.value,
                    "platform": "Telegram",
                },
                "send_time": self.validated_data["message"]["date"] * 1000,
                "conversation": self.validated_data["message"]["chat"]["id"],
            }
        )
        s.is_valid(raise_exception=True)
        return s.save()
