import os

from django.apps import AppConfig

from back.utils import is_migrating, is_celery_worker

from logging import getLogger
from back.utils.celery import recache_models

logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        if is_migrating() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from .signals import on_llm_config_change # noqa
        # from back.apps.language_model.tasks import generate_embeddings_task, llm_query_task, build_index

        # # Making sure that all the Knowledge Items have an embedding for each RAG config
        # RAGConfig = self.get_model("RAGConfig")
        # Embedding = self.get_model("Embedding")
        # KnowledgeItem = self.get_model("KnowledgeItem")

        # # gather all those items that have no embeddings grouped by rag config:
        # changes = False
        # print(f'Len RAGConfig.objects.all(): {len(RAGConfig.objects.all())}')
        # for rag_config in RAGConfig.objects.all():

        #     # # Get the primary keys of KnowledgeItems that already have an associated embedding for the current RAGConfig.
        #     # ki_pks_with_embeddings = Embedding.objects.filter(
        #     #     knowledge_item__knowledge_base=rag_config.knowledge_base,
        #     #     rag_config=rag_config
        #     # ).values_list("knowledge_item__pk", flat=True)

        #     # # Fetch KnowledgeItem instances associated with the current RAGConfig's knowledge base
        #     # # but do not yet have an associated Embedding.
        #     # kis_without_embeddings = KnowledgeItem.objects.filter(
        #     #     knowledge_base=rag_config.knowledge_base
        #     # ).exclude(pk__in=ki_pks_with_embeddings)

        #     # if kis_without_embeddings.exists():
        #     #     changes = True
        #     #     logger.info(f"Generating embeddings for RAG config:{rag_config} #KI {kis_without_embeddings.count()}")
        #     #     generate_embeddings_task.delay(list(kis_without_embeddings.values_list("pk", flat=True)), rag_config.pk)

        #     logger.info(f"Generating index for RAG config:{rag_config}")
        #     build_index.delay(rag_config.pk, recache_models=False, caller='DatasetConfig.ready') 
        #     changes = True

        # if changes:
        #     recache_models("DatasetConfig.ready")
