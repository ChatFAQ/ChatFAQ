import time

from rest_framework import serializers

from back.apps.broker.consumers.message_types import (
    ParseMessageType,
    RPCMessageType,
    RPCNodeType,
)
from back.apps.broker.models.message import AgentType


class CtxSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)
    user_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)


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
    stack_id = serializers.CharField(max_length=255)
    stack = serializers.JSONField(default=dict)
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

    llm_config_name = serializers.CharField()
    conversation_id = serializers.CharField()
    bot_channel_name = serializers.CharField()
    messages = serializers.ListField(child=serializers.DictField())
    temperature = serializers.FloatField(default=0.7, required=False)
    max_tokens = serializers.IntegerField(default=1024, required=False)
    seed = serializers.IntegerField(default=42, required=False)
    streaming = serializers.BooleanField(default=True)


class RPCRAGRequestSerializer(serializers.Serializer):
    """
    Represents the RAG requests coming from the RPC server
    Attributes
    ----------
    rag_config_name: str
        The name of the RAG Config to use in the LLM to generate the text from
    conversation_id: str
        The conversation id to which the LLM response belongs
    bot_channel_name: str
        The bot channel name to which the LLM response should be sent back
    input_text: str
        The input text to generate the text from, it could be None in which case the LLM will generate a text from the previous messages passed as a context
    use_conversation_context: bool
        If True the LLM will use the previous messages as a context to generate the text (if the input_text is None this should be always True)
    streaming: bool
        Whether the LLM response should be streamed or not
    only_context: bool
        If True the LLM will only return the sources and no generation will be done
    """

    rag_config_name = serializers.CharField()
    conversation_id = serializers.CharField()
    bot_channel_name = serializers.CharField()
    input_text = serializers.CharField(
        allow_null=True, allow_blank=True, required=False
    )
    use_conversation_context = serializers.BooleanField(default=True)
    streaming = serializers.BooleanField(default=True)
    only_context = serializers.BooleanField(default=False)

    # If the input_text is None then use_conversation_context should always be True, check for that:
    def validate(self, attrs):
        if not attrs.get("input_text") and not attrs.get("use_conversation_context"):
            raise serializers.ValidationError(
                "If the input_text is None then use_conversation_context should be always True"
            )
        return attrs


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
    """

    name = serializers.CharField(max_length=255)
    definition = serializers.JSONField(default=dict)


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
    )  # data = {rag_config_name, input_text, use_conversation_context, conversation_id, bot_channel_name}


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
