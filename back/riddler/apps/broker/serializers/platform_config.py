from rest_framework import serializers

from ..models.platform_config import PlatformConfig


class PlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformConfig
        fields = "__all__"
