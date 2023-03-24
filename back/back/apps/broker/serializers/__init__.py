from rest_framework import serializers


class TransmitterSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class ConversationSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class ConversationsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))
