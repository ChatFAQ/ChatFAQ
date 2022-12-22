from rest_framework import serializers

from .models import FSMDefinition


class FSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSMDefinition
        fields = "__all__"
