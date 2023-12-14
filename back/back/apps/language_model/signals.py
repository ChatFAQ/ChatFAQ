from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from logging import getLogger

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig
from back.apps.language_model.models.data import KnowledgeItem, Embedding
from back.utils.celery import recache_models
from back.apps.language_model.tasks import generate_embeddings_task

logger = getLogger(__name__)


@receiver(post_save, sender=LLMConfig)
@receiver(post_delete, sender=LLMConfig)
def on_llm_config_change(instance, *args, **kwargs):
    # if the llm instance belongs to a RAGConfig, then we need to reload the models
    rag_configs = RAGConfig.objects.filter(llm_config=instance)
    if rag_configs.exists():
        recache_models("on_llm_config_change")

@receiver(post_save, sender=RAGConfig)
@receiver(post_delete, sender=RAGConfig)
def on_rag_config_change(instance, *args, **kwargs):
    recache_models("on_rag_config_change")

@receiver(post_save, sender=KnowledgeItem)
def on_knowledge_item_change(instance, *args, **kwargs):
    # if the knowledge_base of the knowledge item belongs to a RAGConfig, then we need to generate the embeddings for this knowledge item and reload the models
    # First, remove the embeddings for this knowledge item
    Embedding.objects.filter(knowledge_item=instance).delete()
    rag_configs = RAGConfig.objects.filter(knowledge_base=instance.knowledge_base)
    if rag_configs.exists():
        for rag_config in rag_configs:
            generate_embeddings_task.delay(ki_ids=[instance.id], rag_config_id=rag_config.id, recache_models=False)
    recache_models("on_knowledge_item_change")
