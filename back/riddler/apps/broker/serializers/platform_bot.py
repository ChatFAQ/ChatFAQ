from rest_framework import serializers

from ..models.platform_bot import PlatformBot


class PlatformBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformBot
        fields = "__all__"
