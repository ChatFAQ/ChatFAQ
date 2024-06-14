from rest_framework import serializers
from back.apps.widget.models import Widget, Theme


class WidgetSerializer(serializers.ModelSerializer):
    # method field css:
    css = serializers.SerializerMethodField()

    class Meta:
        model = Widget
        fields = "__all__"

    def get_css(self, obj):
        css = ":root {"
        if obj.theme:
            for css_var in obj.theme.data:
                if type(obj.theme.data[css_var]) is dict:
                    css += f"--{css_var}-light: {obj.theme.data[css_var]['light']};"
                    css += f"--{css_var}-dark: {obj.theme.data[css_var]['dark']};"
                else:
                    css += f"--{css_var}: {obj.theme.data[css_var]};"
        css += "}"

        return css


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"