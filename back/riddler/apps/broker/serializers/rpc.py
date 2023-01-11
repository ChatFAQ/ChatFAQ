from rest_framework import serializers


class CtxSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)


class PayloadSerializer(serializers.Serializer):
    score = serializers.FloatField()
    data = serializers.JSONField(default=dict)


class RPCResponseSerializer(serializers.Serializer):
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
    payload = serializers.JSONField(default=dict)
