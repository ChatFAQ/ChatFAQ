from rest_framework import serializers
from django.apps import apps


class IdSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = apps.get_model('broker', 'Vote')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('broker', 'Message')
