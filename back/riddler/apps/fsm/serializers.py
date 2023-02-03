from rest_framework import serializers

from .models import FSMDefinition
from ...common.serializers import DynamicFieldsSerializerMixin


class FSMSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = FSMDefinition
        fields = "__all__"
