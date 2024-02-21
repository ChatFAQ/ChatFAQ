from django.contrib import admin

from .models.message import Message, UserFeedback
from .models import ConsumerRoundRobinQueue, RemoteSDKParsers


class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation_id", "sender_type", "payload_text", "created_date"]

    def payload_text(self, obj):
        payload = obj.stack[0]['payload']
        if isinstance(payload, str):
            return payload
        else:
            return payload['model_response']

    def sender_type(self, obj):
        return obj.sender["type"]


class UserFeedbackAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(ConsumerRoundRobinQueue)
admin.site.register(RemoteSDKParsers)
