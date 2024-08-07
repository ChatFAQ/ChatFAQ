# Generated by Django 4.1.13 on 2024-06-12 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("language_model", "0054_alter_datasource_splitter_alter_raytaskstate_state"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalpromptconfig",
            old_name="system_prefix",
            new_name="system_prompt",
        ),
        migrations.RenameField(
            model_name="promptconfig",
            old_name="system_prefix",
            new_name="system_prompt",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="assistant_end",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="assistant_tag",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="system_end",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="system_tag",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="user_end",
        ),
        migrations.RemoveField(
            model_name="historicalpromptconfig",
            name="user_tag",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="assistant_end",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="assistant_tag",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="system_end",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="system_tag",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="user_end",
        ),
        migrations.RemoveField(
            model_name="promptconfig",
            name="user_tag",
        ),
    ]