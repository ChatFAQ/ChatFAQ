from django.apps import apps
from rest_framework import serializers

from back.apps.broker.models.message import Message, AdminReviewValue, AgentType


class IdSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "UserFeedback")


class ConsumerRoundRobinQueueSerializer(serializers.ModelSerializer):
    fsm_name = serializers.SerializerMethodField()

    def get_fsm_name(self, obj):
        from back.apps.fsm.models import FSMDefinition
        return FSMDefinition.objects.get(id=obj.rr_group_key).name

    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "ConsumerRoundRobinQueue")


class AdminReviewSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "AdminReview")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model("broker", "Message")
        fields = "__all__"


class ConversationMessagesSerializer(serializers.ModelSerializer):
    msgs_chain = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_msgs_chain(self, obj):
        return [MessageSerializer(m).data for m in obj.get_msgs_chain()]


class ConversationSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_user_id(self, obj):
        for msg in Message.objects.filter(conversation=obj).order_by("created_date"):
            if msg.sender and msg.sender.get("type") == AgentType.human.value:
                return msg.sender.get("id")
            if msg.receiver and msg.receiver.get("type") == AgentType.human.value:
                return msg.receiver.get("id")



class AdminReviewValue(serializers.Serializer):
    value = serializers.ChoiceField(
        required=True, choices=[n.value for n in AdminReviewValue], allow_null=True
    )
    knowledge_item_id = serializers.CharField(required=True, max_length=255)


class AdminReviewSerializer(serializers.ModelSerializer):
    ki_review_data = serializers.ListField(child=AdminReviewValue(), required=False, allow_null=True)

    class Meta:
        from back.apps.broker.models.message import AdminReview  # TODO: CI

        model = AdminReview
        fields = "__all__"


class StatsSerializer(serializers.Serializer):
    min_date = serializers.DateField(required=False, allow_null=True)
    max_date = serializers.DateField(required=False, allow_null=True)
    granularity = serializers.ChoiceField(
        required=False, choices=["year", "quarter", "month", "week", "day", "date", "time", "hour", "minute", "second"], default="day"
    )
