from rest_framework import serializers

from back.apps.broker.consumers.message_types import RPCMessageType, RPCNodeType


class CtxSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)


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


class LLMRequestSerializer(serializers.Serializer):
    rag_config_name = serializers.CharField()
    input_text = serializers.CharField()
    conversation_id = serializers.CharField()
    bot_channel_name = serializers.CharField()


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
    Represents any message coming from the RPC server
    Attributes
    ----------
    type: str
        So far there is only 2 types: 'fsm_def' for registering/declaring FSM Definition & 'rpc_result' results of the
        Remote Procedure Calls
    data: dict
        The RPC response payload
    """

    type = serializers.ChoiceField(choices=[n.value for n in RPCMessageType])
    data = serializers.JSONField(default=dict)
