from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from logging import getLogger

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig
from back.apps.language_model.models.data import KnowledgeItem
from back.utils.celery import recache_models

logger = getLogger(__name__)


@receiver(post_save, sender=LLMConfig)
@receiver(post_delete, sender=LLMConfig)
def on_llm_config_change(instance, *args, **kwargs):
    # if the llm instance belongs to a RAGConfig, then we need to reload the models
    rag_configs = RAGConfig.objects.filter(llm_config=instance)
    if rag_configs.exists():
        recache_models("on_llm_config_change")


@receiver(post_delete, sender=RAGConfig)
def on_rag_config_change(instance, *args, **kwargs):
    recache_models("on_rag_config_change")
