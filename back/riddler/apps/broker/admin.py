from django.contrib import admin

from .models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ["payload_text", "transmitter_type", "conversation"]

    def payload_text(self, obj):
        return obj.payload["text"]

    def transmitter_type(self, obj):
        return obj.transmitter["type"]


admin.site.register(Message, MessageAdmin)
