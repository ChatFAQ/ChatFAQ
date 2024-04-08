import os
from django.apps import AppConfig
from back.utils import is_migrating, is_scraping
from back.utils.celery import is_celery_worker
from back.utils.ray_connection import initialize_or_check_ray
from logging import getLogger


logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        if is_migrating() or is_scraping() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from back.apps.language_model.signals import on_rag_config_change, on_celery_task_signal  # noqa
        from back.apps.language_model.models.enums import IndexStatusChoices
        from back.apps.language_model.tasks import launch_rag_deployment_task

        if not os.environ.get('DEBUG') or os.environ.get('RUN_MAIN'):  # only start ray on the main thread

            storages_mode = os.environ.get("STORAGES_MODE", "local")
            remote_ray_cluster = os.getenv("RAY_CLUSTER", "False") == "True"

            # raise error if we are in local storage mode and we are trying to use a remote ray cluster
            if storages_mode == "local" and remote_ray_cluster:
                raise ValueError("Cannot use a remote ray cluster with local storage mode, please set STORAGES_MODE to s3 or do")


            initialize_or_check_ray()

            RAGConfig = self.get_model("RAGConfig")

            # Now we launch the deployment of the RAGs
            for rag_config in RAGConfig.enabled_objects.all():
                if rag_config.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
                    logger.info(f"Launching RAG deployment for {rag_config.name}")
                    launch_rag_deployment_task.delay(rag_config.id)


