# Generated by Django 4.1.12 on 2023-11-13 12:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("language_model", "0032_remove_intent_knowledge_base"),
    ]

    operations = [
        migrations.AlterField(
            model_name="llmconfig",
            name="llm_type",
            field=models.CharField(
                choices=[
                    ("local_cpu", "Local CPU Model"),
                    ("local_gpu", "Local GPU Model"),
                    ("vllm", "VLLM Client"),
                    ("openai", "OpenAI Model"),
                    ("claude", "Claude Model"),
                ],
                default="local_gpu",
                max_length=10,
            ),
        ),
    ]
