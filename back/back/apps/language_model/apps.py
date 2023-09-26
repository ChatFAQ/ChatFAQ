import os

from django.apps import AppConfig

from back.utils import is_migrating, is_celery_worker

from logging import getLogger

logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        if is_migrating() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from .signals import on_llm_config_change, on_embedding_delete # noqa
        from back.apps.language_model.tasks import generate_embeddings_task, llm_query_task

        # Making sure that all the Knowledge Items have an embedding for each RAG config
        RAGConfig = self.get_model("RAGConfig")
        Embedding = self.get_model("Embedding")
        KnowledgeItem = self.get_model("KnowledgeItem")
        # gather all those items that have no embeddings grouped by rag config:
        changes = False
        for rag_config in RAGConfig.objects.all():
            ki_pks = Embedding.objects.filter(
                knowledge_item__knowledge_base=rag_config.knowledge_base,
                rag_config=rag_config
            ).values_list("knowledge_item__pk", flat=True)

            kis = KnowledgeItem.objects.exclude(
                pk__in=ki_pks,
            )
            logger.info(f"Generating embeddings for RAG config:{rag_config} #KI {kis.count()}")
            if kis.exists():
                changes = True
                generate_embeddings_task.delay(list(kis.values_list("pk", flat=True)), rag_config.pk)
        if changes:
            llm_query_task.delay(recache_models=True)
