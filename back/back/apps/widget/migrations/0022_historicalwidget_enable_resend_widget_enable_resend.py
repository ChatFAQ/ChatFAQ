# Generated by Django 4.2.16 on 2024-12-30 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "widget",
            "0021_rename_hide_theme_mode_historicalwidget_disable_day_night_mode_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalwidget",
            name="enable_resend",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="widget",
            name="enable_resend",
            field=models.BooleanField(default=False),
        ),
    ]
