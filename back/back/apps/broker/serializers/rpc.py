import time

from rest_framework import serializers
from back.apps.broker.models.message import AgentType, StackPayloadType
from back.apps.broker.serializers.messages import MessageSerializer
from back.apps.broker.consumers.message_types import RPCMessageType, ParseMessageType, RPCNodeType
from back.apps.broker.models.message import Message
from back.apps.language_model.models import RAGConfig


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

    def save_as_mml(self, **kwargs):
        if not self.is_valid():
            raise serializers.ValidationError("RPCResultSerializer is not valid")
        if self.validated_data["node_type"] != RPCNodeType.action.value:
            raise serializers.ValidationError("RPCResultSerializer is not an action")

        # Check if extists already a message with the same stack_id, if so we append the new stack to the existing one
        message = Message.objects.filter(stack_id=self.validated_data["stack_id"]).first()
        if message is not None and self.validated_data['stack'][0]["type"] == StackPayloadType.lm_generated_text.value:
            more_model_response = self.validated_data["stack"][0]['payload']['model_response']
            old_payload = message.stack[0]['payload']
            self.validated_data["stack"][0]['payload'].update(old_payload)
            self.validated_data["stack"][0]['payload']['model_response'] = old_payload['model_response'] + more_model_response
            message.stack = self.validated_data["stack"]
            message.last = self.validated_data["last"]
            message.save()
            return message
        else:
            data = {
                "sender": {
                    "type": AgentType.bot.value,
                },
                "confidence": 1,
                "stack": self.validated_data["stack"],
                "stack_id": self.validated_data["stack_id"],
                "last": self.validated_data["last"],
                "conversation": self.validated_data["ctx"]["conversation_id"],
                "send_time": int(time.time() * 1000),
            }
            if self.validated_data['stack'][0]["type"] == StackPayloadType.lm_generated_text.value:
                rag_config_id = RAGConfig.objects.get(name=self.validated_data['stack'][0]['payload']['rag_config_name']).id
                data['stack'][0]['payload']["rag_config_id"] = rag_config_id
            if self.validated_data["ctx"]["user_id"] is not None:
                data["receiver"] = {"type": AgentType.human.value, "id": self.validated_data["ctx"]["user_id"]}
            serializer = MessageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.save(**kwargs)


class LLMRequestSerializer(serializers.Serializer):
    rag_config_name = serializers.CharField()
    input_text = serializers.CharField()
    conversation_id = serializers.CharField()
    bot_channel_name = serializers.CharField()
    user_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)


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
