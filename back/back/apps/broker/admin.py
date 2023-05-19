from django.contrib import admin

from .models.message import Message, Vote


class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender_type", "conversation", "stacks", "created_date"]

    def payload_text(self, obj):
        return obj.payload["text"]

    def sender_type(self, obj):
        return obj.sender["type"]


class VoteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(Vote, VoteAdmin)
