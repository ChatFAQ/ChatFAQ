from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from logging import getLogger

from back.apps.language_model.models.rag_pipeline import LLMConfig
from back.apps.language_model.models.data import Embedding
from back.apps.language_model.tasks import llm_query_task


logger = getLogger(__name__)


@receiver(post_save, sender=LLMConfig)
@receiver(post_delete, sender=LLMConfig)
def on_llm_config_change(instance, *args, **kwargs):
    llm_query_task.delay(recache_models=True)


# on post delete of embeddings we need to trigger the llm_query_task
@receiver(post_delete, sender=Embedding)
def on_embedding_delete(instance, *args, **kwargs):
    llm_query_task.delay(recache_models=True)
