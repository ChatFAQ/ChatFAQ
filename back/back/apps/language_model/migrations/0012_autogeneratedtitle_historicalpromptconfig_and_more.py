# Generated by Django 4.1.11 on 2023-09-12 16:59
import uuid

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import fernet_fields.fields
import simple_history.models


def create_uuid(apps, schema_editor):
    GenerationConfig = apps.get_model("language_model", "GenerationConfig")
    for gc in GenerationConfig.objects.all():
        gc.name = uuid.uuid4()
        gc.save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("language_model", "0011_historicalpromptstructure"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutoGeneratedTitle",
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
                ("title", models.TextField()),
                (
                    "embedding",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), blank=True, null=True, size=None
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalPromptConfig",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("system_prefix", models.TextField(blank=True, default="")),
                (
                    "system_tag",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "system_end",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "user_tag",
                    models.CharField(blank=True, default="<|prompt|>", max_length=255),
                ),
                ("user_end", models.CharField(blank=True, default="", max_length=255)),
                (
                    "assistant_tag",
                    models.CharField(blank=True, default="<|answer|>", max_length=255),
                ),
                (
                    "assistant_end",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("n_contexts_to_use", models.IntegerField(default=3)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical prompt config",
                "verbose_name_plural": "historical prompt configs",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="KnowledgeBase",
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
                    "original_file",
                    models.FileField(blank=True, null=True, upload_to=""),
                ),
                (
                    "lang",
                    models.CharField(
                        choices=[
                            ("en", "English"),
                            ("es", "Spanish"),
                            ("fr", "French"),
                        ],
                        default="en",
                        max_length=2,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KnowledgeItem",
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
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("title", models.TextField(blank=True, null=True)),
                ("content", models.TextField()),
                ("url", models.URLField(max_length=2083)),
                ("section", models.TextField(blank=True, null=True)),
                ("role", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "embedding",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.FloatField(), blank=True, null=True, size=None
                    ),
                ),
                (
                    "knowledge_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="language_model.knowledgebase",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="LLMConfig",
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
                    "repo_id",
                    models.CharField(default="google/flan-t5-base", max_length=100),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("training", "Training"),
                            ("trained", "Trained"),
                        ],
                        default="created",
                        max_length=10,
                    ),
                ),
                (
                    "ggml_model_filename",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "model_config",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "auth_token",
                    fernet_fields.fields.EncryptedCharField(
                        blank=True, max_length=255, null=True
                    ),
                ),
                ("load_in_8bit", models.BooleanField(default=False)),
                ("use_fast_tokenizer", models.BooleanField(default=True)),
                ("trust_remote_code_tokenizer", models.BooleanField(default=False)),
                ("trust_remote_code_model", models.BooleanField(default=False)),
                (
                    "revision",
                    models.CharField(
                        blank=True, default="main", max_length=255, null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PromptConfig",
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
                ("system_prefix", models.TextField(blank=True, default="")),
                (
                    "system_tag",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "system_end",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "user_tag",
                    models.CharField(blank=True, default="<|prompt|>", max_length=255),
                ),
                ("user_end", models.CharField(blank=True, default="", max_length=255)),
                (
                    "assistant_tag",
                    models.CharField(blank=True, default="<|answer|>", max_length=255),
                ),
                (
                    "assistant_end",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("n_contexts_to_use", models.IntegerField(default=3)),
            ],
        ),
        migrations.CreateModel(
            name="RAGConfig",
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
            ],
        ),
        migrations.RemoveField(
            model_name="historicalpromptstructure",
            name="history_user",
        ),
        migrations.RemoveField(
            model_name="historicalpromptstructure",
            name="model",
        ),
        migrations.RemoveField(
            model_name="item",
            name="dataset",
        ),
        migrations.RemoveField(
            model_name="model",
            name="dataset",
        ),
        migrations.RemoveField(
            model_name="promptstructure",
            name="model",
        ),
        migrations.RemoveField(
            model_name="utterance",
            name="item",
        ),
        migrations.RemoveField(
            model_name="generationconfig",
            name="model",
        ),
        migrations.AddField(
            model_name="generationconfig",
            name="name",
            field=models.CharField(max_length=255, blank=True, null=True),
            preserve_default=False,
        ),
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name='generationconfig',
            name='name',
            field=models.UUIDField(max_length=255, unique=True)
        ),
        migrations.DeleteModel(
            name="Dataset",
        ),
        migrations.DeleteModel(
            name="HistoricalPromptStructure",
        ),
        migrations.DeleteModel(
            name="Item",
        ),
        migrations.DeleteModel(
            name="Model",
        ),
        migrations.DeleteModel(
            name="PromptStructure",
        ),
        migrations.DeleteModel(
            name="Utterance",
        ),
        migrations.AddField(
            model_name="ragconfig",
            name="generation_config",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="language_model.generationconfig",
            ),
        ),
        migrations.AddField(
            model_name="ragconfig",
            name="knowledge_base",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.knowledgebase",
            ),
        ),
        migrations.AddField(
            model_name="ragconfig",
            name="llm_config",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="language_model.llmconfig",
            ),
        ),
        migrations.AddField(
            model_name="ragconfig",
            name="prompt_config",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="language_model.promptconfig",
            ),
        ),
        migrations.AddField(
            model_name="autogeneratedtitle",
            name="knowledge_item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.knowledgeitem",
            ),
        ),
    ]
