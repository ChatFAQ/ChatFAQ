from rest_framework import serializers

from riddler.apps.broker.models.rpc import RPCResponse


class CtxSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)


class PayloadSerializer(serializers.Serializer):
    score = serializers.FloatField()
    data = serializers.JSONField(default=dict)


class RPCResponseSerializer(serializers.ModelSerializer):
    ctx = CtxSerializer()
    payload = PayloadSerializer()

    class Meta:
        model = RPCResponse
        fields = "__all__"
