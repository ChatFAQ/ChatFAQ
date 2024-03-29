# Generated by Django 4.1.11 on 2023-09-20 12:59

from django.db import migrations, models
import django.db.models.deletion


def create_retriever_config_if_there_is_none(apps, schema_editor):
    RetrieverConfig = apps.get_model("language_model", "RetrieverConfig")
    if RetrieverConfig.objects.count() == 0:
        r = RetrieverConfig.objects.create(name="default")
        r.save()


class Migration(migrations.Migration):
    dependencies = [
        ("language_model", "0020_alter_llmconfig_llm_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="RetrieverConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "model_name",
                    models.CharField(default="intfloat/e5-small-v2", max_length=255),
                ),
                ("batch_size", models.IntegerField(default=1)),
                (
                    "device",
                    models.CharField(
                        choices=[("cpu", "CPU"), ("cuda", "GPU")],
                        default="cpu",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="ragconfig",
            name="retriever_name",
        ),
        migrations.AlterField(
            model_name="llmconfig",
            name="llm_type",
            field=models.CharField(
                choices=[
                    ("local_cpu", "Local CPU Model"),
                    ("local_gpu", "Local GPU Model"),
                    ("vllm", "VLLM Client"),
                    ("openai", "OpenAI Model"),
                ],
                default="openai",
                max_length=10,
            ),
        ),
        migrations.RunPython(create_retriever_config_if_there_is_none),
        migrations.AddField(
            model_name="ragconfig",
            name="retriever",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="language_model.retrieverconfig",
            ),
            preserve_default=False,
        ),
    ]
