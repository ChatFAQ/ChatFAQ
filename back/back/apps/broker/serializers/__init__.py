from django.apps import apps
from rest_framework import serializers

from back.apps.broker.models import ConsumerRoundRobinQueue
from back.apps.broker.models.message import Message, AdminReviewValue, AgentType
from back.apps.language_model.models import RAGConfig


class IdSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = apps.get_model("broker", "UserFeedback")


class ConsumerRoundRobinQueueSerializer(serializers.ModelSerializer):
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
    mml_chain = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_mml_chain(self, obj):
        return obj.get_mml_chain()


class ConversationSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    rags = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_user_id(self, obj):
        for msg in Message.objects.filter(conversation=obj).order_by("created_date"):
            if msg.sender and msg.sender.get("type") == AgentType.human.value:
                return msg.sender.get("id")
            if msg.receiver and msg.receiver.get("type") == AgentType.human.value:
                return msg.receiver.get("id")

    def get_rags(self, obj):
        # return queryset.filter(message__stack__0__payload__rag_config_id=rag.id).distinct()
        # Get all the messages from this conversation and aggregate all the rag_config_ids:
        rag_ids = Message.objects.filter(
            conversation=obj
        ).filter(
            stack__0__payload__rag_config_id__isnull=False
        ).values_list(
            "stack__0__payload__rag_config_id", flat=True
        ).distinct()
        # get the RAGConfign names from the ids:
        rag_names = list(RAGConfig.objects.filter(id__in=list(rag_ids.all())).values_list("name", flat=True).all())
        return rag_names


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
    rag = serializers.CharField()
    min_date = serializers.DateField(required=False, allow_null=True)
    max_date = serializers.DateField(required=False, allow_null=True)
    granularity = serializers.ChoiceField(
        required=False, choices=["year", "quarter", "month", "week", "day", "date", "time", "hour", "minute", "second"], default="day"
    )
