from django.contrib import admin

from .models.message import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ["transmitter_type", "conversation", "stacks"]

    def payload_text(self, obj):
        return obj.payload["text"]

    def transmitter_type(self, obj):
        return obj.transmitter["type"]


class PlatformBotAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
