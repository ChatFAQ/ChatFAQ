# Generated by Django 4.1.13 on 2023-12-13 18:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("language_model", "0034_ragconfig_disabled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generationconfig",
            name="max_new_tokens",
            field=models.IntegerField(default=512),
        ),
        migrations.AlterField(
            model_name="historicalpromptconfig",
            name="n_contexts_to_use",
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name="promptconfig",
            name="n_contexts_to_use",
            field=models.IntegerField(default=5),
        ),
    ]