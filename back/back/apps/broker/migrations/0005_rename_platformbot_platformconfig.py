# Generated by Django 4.1.4 on 2022-12-22 14:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("fsm", "0002_rename_cachedmachine_cachedfsm_and_more"),
        ("broker", "0004_rename_fsm_platformbot_fsm_def"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PlatformBot",
            new_name="PlatformConfig",
        ),
    ]
