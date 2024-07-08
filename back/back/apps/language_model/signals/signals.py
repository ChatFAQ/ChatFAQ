from django.db.models.signals import post_delete

from logging import getLogger

from django.dispatch import receiver

from back.apps.language_model.models.rag_pipeline import RAGConfig, LLMConfig
from back.apps.language_model.tasks import delete_index_files
from back.apps.language_model.ray_deployments import delete_rag_deployment, delete_serve_app

logger = getLogger(__name__)


@receiver(post_delete, sender=RAGConfig)
def on_rag_config_change(instance, *args, **kwargs):
    s3_index_path = instance.s3_index_path

    if s3_index_path:
        task_name = f"delete_index_files_{instance.name}"
        logger.info(f"Submitting the {task_name} task to the Ray cluster...")
        delete_index_files.options(name=task_name).remote(s3_index_path)

    rag_deploy_name = instance.get_deploy_name()
    task_name = f"delete_rag_deployment_{instance.name}"
    logger.info(f"Submitting the {task_name} task to the Ray cluster...")
    delete_rag_deployment.options(name=task_name).remote(rag_deploy_name)


@receiver(post_delete, sender=LLMConfig)
def on_llm_config_change(instance, *args, **kwargs):
    task_name = f"delete_serve_app_{instance.name}"
    logger.info(f"Submitting the {task_name} task to the Ray cluster...")
    delete_serve_app.options(name=task_name).remote(instance.get_deploy_name())
