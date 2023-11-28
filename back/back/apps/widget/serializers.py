from rest_framework import serializers
from back.apps.widget.models import Widget, Theme


class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = "__all__"


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"
