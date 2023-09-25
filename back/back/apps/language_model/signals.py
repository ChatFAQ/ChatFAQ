from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from logging import getLogger

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig
from back.apps.language_model.models.data import Embedding
from back.apps.language_model.tasks import llm_query_task, generate_embeddings_task


logger = getLogger(__name__)

@receiver(post_save, sender=LLMConfig)
@receiver(post_delete, sender=LLMConfig)
def on_llm_config_change(instance, *args, **kwargs):
    llm_query_task.delay(recache_models=True)

@receiver(post_save, sender=RAGConfig)
def on_rag_config_create(instance, *args, **kwargs):
    logger.info(f"Generating embeddings for RAG config {instance}")
    generate_embeddings_task.delay(instance.pk)
    llm_query_task.delay(recache_models=True)