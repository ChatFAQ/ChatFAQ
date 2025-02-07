from django.contrib import admin

from .models.message import Message, UserFeedback, AdminReview, Conversation
from .models import ConsumerRoundRobinQueue, RemoteSDKParsers
import time


class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation_id", "id", "sender_type", "payload_text", "created_date"]

    def payload_text(self, obj):
        payload = obj.stack[0]['payload'] if obj.stack else ''
        if 'content' in payload and isinstance(payload, dict):
            return payload['content']
        elif 'model_response' in payload and isinstance(payload, dict):
            return payload['model_response']
        else:
            return payload

    def sender_type(self, obj):
        return obj.sender["type"]


class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "message_source", "message_target", "feedback_data"]


class AdminReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "message_id", "gen_review_val", "gen_review_type", "ki_review_data"]


admin.site.register(Message, MessageAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(AdminReview, AdminReviewAdmin)
admin.site.register(Conversation)
admin.site.register(ConsumerRoundRobinQueue)
admin.site.register(RemoteSDKParsers)
