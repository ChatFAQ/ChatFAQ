from io import StringIO
from logging import getLogger
from typing import TYPE_CHECKING

from drf_spectacular.utils import (
    PolymorphicProxySerializer,
    extend_schema_field,
    extend_schema_serializer,
)
from lxml import etree
from lxml.etree import XMLSyntaxError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from back.apps.broker.models.message import AgentType, Satisfaction, StackPayloadType
from back.common.abs.bot_consumers import BotConsumer
from back.common.serializer_fields import JSTimestampField
from back.common.validators import AtLeastNOf, PresentTogether

if TYPE_CHECKING:
    from back.apps.broker.models.message import Message

logger = getLogger(__name__)


def custom_postprocessing_hook(result, generator, request, public):
    return result


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
    id = serializers.CharField(required=False, max_length=255)
    first_name = serializers.CharField(required=False, max_length=255)
    last_name = serializers.CharField(required=False, max_length=255)
    type = serializers.ChoiceField(choices=[n.value for n in AgentType])
    platform = serializers.CharField(required=False, max_length=255)

    # class Meta:
    #
    #     validators = [
    #         PresentTogether(fields=[{"type": AgentType.human.value}, "platform"])
    #     ]


class QuickReplySerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    id = serializers.CharField(max_length=255)
    meta = serializers.JSONField(required=False)


# ----------- Payload's types -----------


class TextPayload(serializers.Serializer):
    payload = serializers.CharField()


class Reference(serializers.Serializer):
    knowledge_item_id = serializers.CharField(required=True)
    url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class LMGeneratedTextPayload(serializers.Serializer):
    class _LMGeneratedTextPayload(serializers.Serializer):
        model_response = serializers.CharField(trim_whitespace=False, allow_blank=True)
        rag_config_name = serializers.CharField()
        references = Reference(many=True, required=False, allow_null=True)
        lm_msg_id = serializers.CharField()

    payload = _LMGeneratedTextPayload()


class HTMLPayload(serializers.Serializer):
    @staticmethod
    def html_syntax_validator(value):
        try:
            etree.parse(StringIO(value), etree.HTMLParser(recover=False))
        except XMLSyntaxError:
            raise serializers.ValidationError("This field must be valid HTML.")

    payload = serializers.CharField(validators=[html_syntax_validator])


class ImagePayload(serializers.Serializer):
    payload = serializers.URLField()


class SatisfactionPayload(serializers.Serializer):
    payload = serializers.ChoiceField(
        required=False, choices=[n.value for n in Satisfaction], allow_null=True
    )


class QuickRepliesPayload(serializers.Serializer):
    payload = QuickReplySerializer(required=False, many=True)


# ----------- --------------- -----------


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="Payload",
        resource_type_field_name="payload",
        serializers={
            "TextPayload": TextPayload,
            "LMGeneratedTextPayload": LMGeneratedTextPayload,
            "HTMLPayload": HTMLPayload,
            "ImagePayload": ImagePayload,
            "SatisfactionPayload": SatisfactionPayload,
            "QuickRepliesPayload": QuickRepliesPayload,
        },
    )
)
class Payload(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class MessageStackSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[n.value for n in StackPayloadType])
    payload = Payload()
    id = serializers.CharField(required=False, max_length=255)
    meta = serializers.JSONField(required=False)

    def validate(self, data):
        if data.get("type") == StackPayloadType.text.value:
            s = TextPayload(data=data)
        elif data.get("type") == StackPayloadType.lm_generated_text.value:
            s = LMGeneratedTextPayload(data=data)
        elif data.get("type") == StackPayloadType.html.value:
            s = HTMLPayload(data=data)
        elif data.get("type") == StackPayloadType.image.value:
            s = ImagePayload(data=data)
        elif data.get("type") == StackPayloadType.satisfaction.value:
            s = SatisfactionPayload(data=data)
        elif data.get("type") == StackPayloadType.quick_replies.value:
            s = QuickRepliesPayload(data=data)
        else:
            # TODO: support any other structure? just mark it as a JSONField and let the user handle it in the FE?
            #  letting the database record the payload as unknow structure?
            raise serializers.ValidationError(f'type not supported {data.get("type")}')
        s.is_valid(raise_exception=True)
        data["payload"] = s.validated_data["payload"]
        return data


class MessageSerializer(serializers.ModelSerializer):
    stack = serializers.ListField(child=MessageStackSerializer())
    stack_id = serializers.CharField(required=False, max_length=255)
    last = serializers.BooleanField(default=False)
    sender = AgentSerializer()
    receiver = AgentSerializer(required=False)
    send_time = JSTimestampField()

    class Meta:
        from back.apps.broker.models.message import Message  # TODO: CI

        model = Message
        fields = "__all__"

    def validate_prev(self, prev):
        """
        - There should be only one message with prev set to None
        - Prev should be None or belonging to the same conversation
        """
        from back.apps.broker.models.message import Message  # TODO: CI

        # It seems we are implementing "UniqueValidator" but nor really, because this will also fail for when value=None
        # and another message also already have value=None while UniqueValidator will not fail on this specific use case
        if Message.objects.filter(
            conversation=self.initial_data["conversation"], prev=prev
        ).first():
            raise ValidationError(
                f"prev should be always unique for the same conversation"
            )
        if prev and prev.conversation != str(self.initial_data["conversation"]):
            raise ValidationError(f"prev should belong to the same conversation")
