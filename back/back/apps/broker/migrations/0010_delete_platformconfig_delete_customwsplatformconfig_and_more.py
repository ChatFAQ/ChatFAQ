# Generated by Django 4.1.4 on 2023-01-24 17:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("broker", "0009_alter_platformconfig_platform_meta"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PlatformConfig",
        ),
        migrations.DeleteModel(
            name="CustomWSPlatformConfig",
        ),
        migrations.DeleteModel(
            name="TelegramPlatformConfig",
        ),
    ]
