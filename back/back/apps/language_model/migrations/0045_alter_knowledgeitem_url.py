# Generated by Django 4.1.13 on 2024-02-20 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("language_model", "0044_remove_knowledgebase_chunk_overlap_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="knowledgeitem",
            name="url",
            field=models.URLField(blank=True, max_length=2083, null=True),
        ),
    ]