from rest_framework import serializers


class ConversationsSerializer(serializers.Serializer):
    transmitter_id = serializers.CharField(max_length=255)


class ConversationSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(max_length=255)
