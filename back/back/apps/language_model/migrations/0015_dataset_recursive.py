# Generated by Django 4.1.10 on 2023-09-12 17:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("language_model", "0014_alter_dataset_strategy"),
    ]

    operations = [
        migrations.AddField(
            model_name="KnowledgeBase",
            name="recursive",
            field=models.BooleanField(default=True),
        ),
    ]
