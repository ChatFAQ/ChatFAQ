# Generated by Django 4.2.16 on 2024-12-31 08:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("broker", "0042_remove_message_file_request_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfeedback",
            name="star_rating",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AddField(
            model_name="userfeedback",
            name="star_rating_max",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AlterField(
            model_name="userfeedback",
            name="value",
            field=models.CharField(
                blank=True,
                choices=[("positive", "Positive"), ("negative", "Negative")],
                max_length=255,
                null=True,
            ),
        ),
    ]
