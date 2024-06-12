# Generated by Django 4.1.13 on 2024-06-12 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("language_model", "0056_remove_generationconfig_max_new_tokens_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="llmconfig",
            name="ggml_llm_filename",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="load_in_8bit",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="model_config",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="revision",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="trust_remote_code_model",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="trust_remote_code_tokenizer",
        ),
        migrations.RemoveField(
            model_name="llmconfig",
            name="use_fast_tokenizer",
        ),
        migrations.AddField(
            model_name="llmconfig",
            name="base_url",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="llmconfig",
            name="llm_name",
            field=models.CharField(default="gpt-4o", max_length=100),
        ),
    ]
