# Generated by Django 4.1.13 on 2024-03-15 12:44

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("broker", "0033_remotesdkparsers"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userfeedback",
            old_name="feedback",
            new_name="feedback_comment",
        ),
        migrations.AddField(
            model_name="userfeedback",
            name="feedback_selection",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, null=True, size=None
            ),
        ),
    ]
