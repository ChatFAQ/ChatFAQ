from django.apps import apps
from rest_framework import serializers

from back.apps.broker.models.message import Message


class IdSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "UserFeedback")


class AdminReviewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "AdminReview")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model("broker", "Message")
        fields = "__all__"


class ConversationMessagesSerializer(serializers.ModelSerializer):
    mml_chain = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_mml_chain(self, obj):
        return obj.get_mml_chain(group_by_stack=True)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"
