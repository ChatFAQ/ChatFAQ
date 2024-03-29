# Generated by Django 4.1.13 on 2024-02-29 16:20

from django.db import migrations, models
import django.db.models.deletion
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ("broker", "0033_remotesdkparsers"),
        ("language_model", "0047_alter_ragconfig_s3_index_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="autogeneratedtitle",
            name="embedding",
            field=pgvector.django.VectorField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="autogeneratedtitle",
            name="knowledge_item",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.knowledgeitem",
            ),
        ),
        migrations.AlterField(
            model_name="embedding",
            name="embedding",
            field=pgvector.django.VectorField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="embedding",
            name="knowledge_item",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.knowledgeitem",
            ),
        ),
        migrations.AlterField(
            model_name="embedding",
            name="rag_config",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.ragconfig",
            ),
        ),
        migrations.AlterField(
            model_name="intent",
            name="auto_generated",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name="intent",
            name="knowledge_item",
            field=models.ManyToManyField(
                blank=True, editable=False, to="language_model.knowledgeitem"
            ),
        ),
        migrations.AlterField(
            model_name="intent",
            name="message",
            field=models.ManyToManyField(
                blank=True, editable=False, to="broker.message"
            ),
        ),
        migrations.AlterField(
            model_name="intent",
            name="suggested_intent",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name="knowledgeitem",
            name="data_source",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.datasource",
            ),
        ),
        migrations.AlterField(
            model_name="knowledgeitem",
            name="message",
            field=models.ManyToManyField(
                editable=False,
                through="language_model.MessageKnowledgeItem",
                to="broker.message",
            ),
        ),
        migrations.AlterField(
            model_name="messageknowledgeitem",
            name="knowledge_item",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="language_model.knowledgeitem",
            ),
        ),
        migrations.AlterField(
            model_name="messageknowledgeitem",
            name="message",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="broker.message",
            ),
        ),
        migrations.AlterField(
            model_name="messageknowledgeitem",
            name="similarity",
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="ragconfig",
            name="index_up_to_date",
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
