from rest_framework import serializers
from django.apps import apps



class TransmitterSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class ConversationSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class ConversationsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('broker', 'Vote')
