from django.contrib import admin

from .models.message import Message, Vote


class MessageAdmin(admin.ModelAdmin):
    list_display = ["transmitter_type", "conversation", "stacks", "created_date"]

    def payload_text(self, obj):
        return obj.payload["text"]

    def transmitter_type(self, obj):
        return obj.transmitter["type"]


class VoteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(Vote, VoteAdmin)
