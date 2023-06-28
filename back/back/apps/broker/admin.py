from django.contrib import admin

from .models.message import Message, UserFeedback
from .models import RPCConsumerRoundRobinQueue


class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender_type", "conversation", "stack", "created_date"]

    def payload_text(self, obj):
        return obj.payload["text"]

    def sender_type(self, obj):
        return obj.sender["type"]


class UserFeedbackAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)
admin.site.register(RPCConsumerRoundRobinQueue)
