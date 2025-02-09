from io import StringIO
from logging import getLogger
from typing import TYPE_CHECKING

from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field
from lxml import etree
from lxml.etree import XMLSyntaxError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from back.apps.broker.models.message import AgentType, Satisfaction
from back.apps.fsm.models import FSMDefinition
from back.common.abs.bot_consumers import BotConsumer
from back.common.serializer_fields import JSTimestampField
from back.config.storage_backends import (
    PrivateMediaLocalStorage,
    select_private_storage,
)

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

class ReferenceKi(serializers.Serializer):
    knowledge_item_id = serializers.CharField(required=True)
    url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    image_urls = serializers.DictField(required=False, allow_null=True, allow_empty=True)

class Reference(serializers.Serializer):
    knowledge_items = ReferenceKi(many=True, required=False, allow_null=True)
    knowledge_item_images = serializers.DictField(required=False, allow_null=True, allow_empty=True)
    knowledge_base_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ToolUse(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    args = serializers.JSONField(required=True)
    text = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ToolResult(serializers.Serializer):
    id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    result = serializers.CharField(required=True)


class MessagePayload(serializers.Serializer):
    content = serializers.SerializerMethodField()
    references = Reference(required=False, allow_null=True)

    @extend_schema_field(
        PolymorphicProxySerializer(
            component_name="MessageContent",
            serializers=[
                serializers.CharField,
                ToolUse,
                ToolResult
            ],
        )
    )
    def get_content(self, obj):
        return obj


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
            "MessagePayload": MessagePayload,
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


class FSMDefinitionField(serializers.Field):
    def to_internal_value(self, data):
        fsm_def = FSMDefinition.get_by_id_or_name(data)
        if fsm_def:
            return fsm_def.id
        raise serializers.ValidationError(f"FSM Definition '{data}' not found.")

    def to_representation(self, value):
        try:
            fsm_def = FSMDefinition.objects.get(id=value)
            return fsm_def.name
        except FSMDefinition.DoesNotExist:
            return None


class MessageStackSerializer(serializers.Serializer):
    type = serializers.CharField(required=True, max_length=255)
    streaming = serializers.BooleanField(default=False)
    payload = Payload(required=False)
    id = serializers.CharField(required=False, max_length=255)
    meta = serializers.JSONField(required=False)
    state = serializers.JSONField(required=False)
    fsm_definition = FSMDefinitionField(required=False, allow_null=True)

    def validate(self, attrs):
        # If it is a file for download and doesn't have a url then we need to return a url to the file so the fsm can download it
        if attrs['type'] == 'file_uploaded' and not attrs.get('payload', {}).get('url') and attrs.get('payload', {}).get('s3_path'):
            storage = select_private_storage()
            if not isinstance(storage, PrivateMediaLocalStorage):
                attrs['payload']['url'] = storage.generate_presigned_url_get(attrs.get('payload', {}).get('s3_path'), expires_in=3600)
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    stack = serializers.ListField(child=MessageStackSerializer())
    stack_id = serializers.CharField(required=False, max_length=255)
    stack_group_id = serializers.CharField(required=False, max_length=255)
    last = serializers.BooleanField(default=False)
    last_chunk = serializers.BooleanField(default=False)
    sender = AgentSerializer()
    receiver = AgentSerializer(required=False)
    send_time = JSTimestampField()
    reviewed = serializers.SerializerMethodField()
    status = serializers.JSONField(required=False, allow_null=True)
    fsm_state = serializers.JSONField(required=False, allow_null=True)

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
                "prev should be always unique for the same conversation"
            )
        if prev and prev.conversation != str(self.initial_data["conversation"]):
            raise ValidationError("prev should belong to the same conversation")

    def get_reviewed(self, obj):
        return obj.completed_review
