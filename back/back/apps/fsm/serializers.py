from rest_framework import serializers

from ...common.serializers import DynamicFieldsSerializerMixin
from .models import FSMDefinition


class FSMSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = FSMDefinition
        fields = "__all__"
