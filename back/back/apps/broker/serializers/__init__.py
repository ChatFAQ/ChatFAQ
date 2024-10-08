from django.apps import apps
from rest_framework import serializers

from back.apps.broker.models.message import Message, AdminReviewValue, AgentType
from back.apps.fsm.models import FSMDefinition


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


def _get_fsm_defs(_, obj):
    """Returns the FSM definitions name"""
    fsm_def_ids = Message.objects.filter(conversation=obj).values_list("stack__0__fsm_definition", flat=True).distinct()
    fsm_def_ids = list(filter(None, fsm_def_ids))
    defs = []
    for fsm_def_id in fsm_def_ids:
        fsm_def = FSMDefinition.objects.filter(id=fsm_def_id).first()
        if fsm_def:
            defs.append(fsm_def.name)
        else:  # If the SDK has overwritten the FSM definition, then the id will be dangling
            defs.append(None)
            # defs.append(fsm_def_id)
    return defs


class ConversationMessagesSerializer(serializers.ModelSerializer):
    msgs_chain = serializers.SerializerMethodField()
    fsm_defs = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_msgs_chain(self, obj):
        return [MessageSerializer(m).data for m in obj.get_msgs_chain()]

    get_fsm_defs = _get_fsm_defs


class ConversationSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    fsm_defs = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("broker", "Conversation")
        fields = "__all__"

    def get_user_id(self, obj):
        for msg in Message.objects.filter(conversation=obj).order_by("created_date"):
            if msg.sender and msg.sender.get("type") == AgentType.human.value:
                return msg.sender.get("id")
            if msg.receiver and msg.receiver.get("type") == AgentType.human.value:
                return msg.receiver.get("id")

    get_fsm_defs = _get_fsm_defs



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
