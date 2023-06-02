from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    model_id = serializers.CharField()
    query = serializers.CharField()
