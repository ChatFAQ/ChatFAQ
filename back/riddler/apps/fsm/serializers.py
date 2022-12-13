from rest_framework import serializers

from .models import FiniteStateMachine


class FSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiniteStateMachine
        fields = "__all__"
