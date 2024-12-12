import time
import mimetypes

from rest_framework import serializers

from back.apps.broker.consumers.message_types import (
    ParseMessageType,
    RPCMessageType,
    RPCNodeType,
)
from back.apps.broker.models.message import AgentType
from back.config.storage_backends import (
    PrivateMediaLocalStorage,
    select_private_storage,
)


class CtxSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)
    user_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    status = serializers.JSONField(default=dict)


class PayloadSerializer(serializers.Serializer):
    score = serializers.FloatField()
    data = serializers.JSONField(default=dict)


class RPCResultSerializer(serializers.Serializer):
    """
    This represent the communication layer between the RPC consumer and the Bot Consumer/View
    Attributes
    ----------
    ctx: dict
        The conversation ctx to which the RPC is giving a result, this json has to have a "conversation_id" key just so
        the RPC Consumer knows to which Bot Consumer/View should send the data
    payload: dict
        The RPC response payload
    """

    ctx = CtxSerializer()
    node_type = serializers.ChoiceField(choices=[n.value for n in RPCNodeType])
    stack_group_id = serializers.CharField(max_length=255)
    stack_id = serializers.CharField(max_length=255)
    stack = serializers.JSONField(default=dict)
    last_chunk = serializers.BooleanField(default=False)
    last = serializers.BooleanField(default=False)

    def validate(self, attrs):
        attrs["sender"] = {"type": AgentType.bot.value}
        attrs["confidence"] = 1
        attrs["send_time"] = int(time.time() * 1000)
        if attrs.get("ctx", {}).get("user_id") is not None:
            attrs["receiver"] = {
                "type": AgentType.human.value,
                "id": attrs["ctx"]["user_id"],
            }

        # Generate presigned URL if the message is a file request
        for ndx, element in enumerate(attrs.get("stack", [])):
            if element["type"] == "file_upload":
                storage = select_private_storage()

                for file_extension in element["payload"].keys():

                    # Generate presigned URL if using S3
                    if not isinstance(storage, PrivateMediaLocalStorage):
                        s3_path = f"uploads/{attrs['ctx']['conversation_id']}/{int(time.time())}"

                        # We receive the file extension from the client, but we need to add the placeholder to the file extension to be able to guess the content type
                        content_type = mimetypes.guess_type(f'placeholder.{file_extension}')[0]
                        attrs['stack'][ndx]['payload'][file_extension]['presigned_url'] = storage.generate_presigned_url(s3_path, content_type=content_type)
                        attrs['stack'][ndx]['payload'][file_extension]['s3_path'] = s3_path
                        attrs['stack'][ndx]['payload'][file_extension]['content_type'] = content_type
                    
        return super().validate(attrs)


class RPCLLMRequestSerializer(serializers.Serializer):
    """
    Represents the LLM requests coming from the RPC server
    Attributes
    ----------
    llm_config_name: str
        The name of the LLM Config to use in the LLM to generate the text from
    conversation_id: str
        The conversation id to which the LLM response belongs
    bot_channel_name: str
        The bot channel name to which the LLM response should be sent back
    messages: List[Dict[str, str]]
        The messages sent from the SDK to generate the text from
    temperature: float
        The temperature to use in the LLM
    max_tokens: int
        The maximum number of tokens to generate
    seed: int
        The seed to use in the LLM
    streaming: bool
        Whether the LLM response should be streamed or not
    """

    llm_config_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    conversation_id = serializers.CharField()
    bot_channel_name = serializers.CharField()
    messages = serializers.ListField(child=serializers.DictField())
    temperature = serializers.FloatField(default=0.7, required=False)
    max_tokens = serializers.IntegerField(default=1024, required=False)
    seed = serializers.IntegerField(default=42, required=False)
    tools = serializers.ListField(
        child=serializers.DictField(), allow_empty=True, required=False, allow_null=True
    )
    tool_choice = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    streaming = serializers.BooleanField(default=True)
    use_conversation_context = serializers.BooleanField(default=True)

    def validate(self, attrs):
        if not attrs.get("messages") and not attrs.get("use_conversation_context"):
            raise serializers.ValidationError(
                "If there are no messages then use_conversation_context should be always True"
            )
        return attrs


class RPCPromptRequestSerializer(serializers.Serializer):
    prompt_config_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    bot_channel_name = serializers.CharField()


class RPCRetrieverRequestSerializer(serializers.Serializer):

    retriever_config_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    bot_channel_name = serializers.CharField()
    query = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    top_k = serializers.IntegerField(default=3)


class RegisterParsersSerializer(serializers.Serializer):
    parsers = serializers.ListSerializer(child=serializers.CharField())


class ParsersFinishSerializer(serializers.Serializer):
    task_id = serializers.CharField()


class RPCFSMDefSerializer(serializers.Serializer):
    """
    Used for when a RPC Server push a FSM definition
    ----------
    name: str
        Name of the new FSM
    definition: dict
        The definition itself
    overwrite: bool
        Whether to overwrite an existing FSM with the same name
    """

    name = serializers.CharField(max_length=255)
    definition = serializers.JSONField(default=dict)
    overwrite = serializers.BooleanField(default=False)
    authentication_required = serializers.BooleanField(default=False)


class RPCResponseSerializer(serializers.Serializer):
    """
    Represents any result coming from the RPC server
    Attributes
    ----------
    type: str
        So far there is only 2 types: 'fsm_def' for registering/declaring FSM Definition & 'rpc_result' results of the
        Remote Procedure Calls
    data: dict
        The RPC response payload
    """

    type = serializers.ChoiceField(choices=[n.value for n in RPCMessageType])
    data = serializers.JSONField(
        default=dict
    )

class ParseResponseSerializer(serializers.Serializer):
    """
    Represents any message coming from the RPC server
    Attributes
    ----------
    type: str
        So far there is only 2 types: 'fsm_def' for registering/declaring FSM Definition & 'rpc_result' results of the
        Remote Procedure Calls
    data: dict
        The RPC response payload
    """

    type = serializers.ChoiceField(choices=[n.value for n in ParseMessageType])
    data = serializers.JSONField(default=dict)
