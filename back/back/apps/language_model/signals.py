from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.signals import before_task_publish, after_task_publish, task_prerun, task_postrun, task_retry, task_success, task_failure, task_internal_error, task_received, task_revoked, task_unknown, task_rejected
from django_celery_results.models import TaskResult

from logging import getLogger

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig
from back.apps.language_model.tasks import delete_index_files_task
from back.utils.celery import recache_models
from django.dispatch import receiver
from celery.signals import (
    before_task_publish, after_task_publish, task_prerun, task_postrun, task_retry, task_success, task_failure,
    task_internal_error, task_received, task_revoked, task_unknown, task_rejected
)

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
    s3_index_path = instance.s3_index_path
    if s3_index_path:
        delete_index_files_task.delay(s3_index_path, recache_models=True)

    else:
        recache_models("on_rag_config_change")


@before_task_publish.connect
@after_task_publish.connect
@task_prerun.connect
@task_postrun.connect
@task_retry.connect
@task_success.connect
@task_internal_error.connect
@task_received.connect
@task_revoked.connect
@task_unknown.connect
@task_rejected.connect
def on_celery_task_signal(sender=None, headers=None, body=None, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("tasks", {'type': 'send.data'})
