# Generated by Django 4.1.13 on 2023-12-04 13:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("widget", "0006_rename_temp_id_widget_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="theme",
            name="data",
            field=models.JSONField(
                default={
                    "chatfaq-color-alertMessage-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#e7e8e9", "light": "#545a64"},
                    },
                    "chatfaq-color-bubbleButton-background": {
                        "section": "colors",
                        "type": "gradient",
                        "value": "linear-gradient(135deg, #CE0578 0%, #463075 100%)",
                    },
                    "chatfaq-color-bubbleButton-background-hover": {
                        "section": "colors",
                        "type": "gradient",
                        "value": "linear-gradient(135deg, #463075 0%, #220D44 100%)",
                    },
                    "chatfaq-color-chat-background": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#4D4160", "light": "#dfdaea"},
                    },
                    "chatfaq-color-chatInput-background": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#3c2d52", "light": "#cac2da"},
                    },
                    "chatfaq-color-chatInput-border": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#1A0438", "light": "#9a8eb5"},
                    },
                    "chatfaq-color-chatInput-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#FFFFFF", "light": "#020C1C"},
                    },
                    "chatfaq-color-chatMessageBot-background": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#3c2d52", "light": "#cac2da"},
                    },
                    "chatfaq-color-chatMessageBot-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#FFFFFF", "light": "#020C1C"},
                    },
                    "chatfaq-color-chatMessageHuman-background": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#1A0438", "light": "#463075"},
                    },
                    "chatfaq-color-chatMessageHuman-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#FFFFFF", "light": "#FFFFFF"},
                    },
                    "chatfaq-color-chatMessageReference-background": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#1A0438", "light": "#4630751a"},
                    },
                    "chatfaq-color-chatMessageReference-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#dfdaea", "light": "#463075"},
                    },
                    "chatfaq-color-chatMessageReferenceTitle-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#aaafb5", "light": "#9a8eb5"},
                    },
                    "chatfaq-color-chatPlaceholder-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#dfdaea", "light": "#020c1c99"},
                    },
                    "chatfaq-color-clipboard-text": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#cac2da", "light": "#9a8eb5"},
                    },
                    "chatfaq-color-darkFilter": {
                        "section": "colors",
                        "type": "color",
                        "value": "#020c1cb3",
                    },
                    "chatfaq-color-loader": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#FFFFFF", "light": "#463075"},
                    },
                    "chatfaq-color-menu-background": {
                        "section": "colors",
                        "type": "gradient",
                        "value": "linear-gradient(135deg, #463075 0%, #220D44 100%)",
                    },
                    "chatfaq-color-menu-border": {
                        "section": "colors",
                        "type": "color",
                        "value": "#4D4160",
                    },
                    "chatfaq-color-menu-scrollColor": {
                        "section": "colors",
                        "type": "color",
                        "value": "#9FFFFF",
                    },
                    "chatfaq-color-menu-text": {
                        "section": "colors",
                        "type": "color",
                        "value": "#FFFFFF",
                    },
                    "chatfaq-color-menuButton-background": {
                        "section": "colors",
                        "type": "color",
                        "value": "#463075",
                    },
                    "chatfaq-color-menuItem-background": {
                        "section": "colors",
                        "type": "color",
                        "value": "#dfdaea1a",
                    },
                    "chatfaq-color-menuItem-background-hover": {
                        "section": "colors",
                        "type": "color",
                        "value": "#1A0438",
                    },
                    "chatfaq-color-menuItem-border-edit": {
                        "section": "colors",
                        "type": "color",
                        "value": "#9FFFFF",
                    },
                    "chatfaq-color-scrollBar": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#463075", "light": "#FFFFFF"},
                    },
                    "chatfaq-color-separator": {
                        "section": "colors",
                        "type": "color",
                        "value": {"dark": "#4D4160", "light": "#46307533"},
                    },
                    "chatfaq-font-body-m": {
                        "section": "body",
                        "type": "font",
                        "value": "normal normal 400 24px/33px 'Open Sans'",
                    },
                    "chatfaq-font-body-m-bold": {
                        "section": "body",
                        "type": "font",
                        "value": "normal normal 600 16px/22px 'Open Sans'",
                    },
                    "chatfaq-font-body-s": {
                        "section": "body",
                        "type": "font",
                        "value": "normal normal 400 14px/19px 'Open Sans'",
                    },
                    "chatfaq-font-body-xl": {
                        "section": "body",
                        "type": "font",
                        "value": "normal normal 400 24px/33px 'Open Sans'",
                    },
                    "chatfaq-font-body-xs": {
                        "section": "body",
                        "type": "font",
                        "value": "normal normal 400 14px/19px 'Open Sans'",
                    },
                    "chatfaq-font-button": {
                        "section": "buttons",
                        "type": "font",
                        "value": "normal normal 600 14px/17px 'Montserrat'",
                    },
                    "chatfaq-font-caption-md": {
                        "section": "captions",
                        "type": "font",
                        "value": "italic normal 600 14px/19px 'Open Sans'",
                    },
                    "chatfaq-font-caption-sm": {
                        "section": "captions",
                        "type": "font",
                        "value": "normal normal 400 12px/16px 'Open Sans'",
                    },
                    "chatfaq-size-bubbleButton": {
                        "section": "body",
                        "type": "font",
                        "value": "60px",
                    },
                }
            ),
        ),
    ]
