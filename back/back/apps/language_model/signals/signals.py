from django.db.models.signals import post_save, post_delete
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django_celery_results.models import TaskResult

from logging import getLogger

from django.dispatch import receiver
from celery.signals import (
    before_task_publish, after_task_publish, task_prerun, task_postrun, task_retry, task_success, task_failure,
    task_internal_error, task_received, task_revoked, task_unknown, task_rejected
)
from back.apps.language_model.models.rag_pipeline import RAGConfig
from back.apps.language_model.tasks import delete_index_files_task, delete_rag_deployment_task

logger = getLogger(__name__)


@receiver(post_delete, sender=RAGConfig)
def on_rag_config_change(instance, *args, **kwargs):
    s3_index_path = instance.s3_index_path
    if s3_index_path:
        delete_index_files_task.delay(s3_index_path)

    rag_deploy_name = instance.get_deploy_name()
    delete_rag_deployment_task.delay(rag_deploy_name)


@before_task_publish.connect
@after_task_publish.connect
@task_prerun.connect
@task_postrun.connect
@task_retry.connect
@task_success.connect
@task_failure.connect
@task_internal_error.connect
@task_received.connect
@task_revoked.connect
@task_unknown.connect
@task_rejected.connect
@receiver(post_save, sender=TaskResult)
def on_celery_task_signal(*args, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("tasks", {'type': 'send.data'})
