import os
from django.apps import AppConfig
from django.conf import settings
from back.utils import is_migrating, is_scraping
from back.utils.celery import is_celery_worker
from back.utils.ray_connection import initialize_or_check_ray, connect_to_ray_cluster
from logging import getLogger
import ray


logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"
    ray_context = None

    def ready(self):
        if is_migrating() or is_scraping() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from back.apps.language_model.signals import on_rag_config_change, on_celery_task_signal  # noqa
        from back.apps.language_model.models.enums import IndexStatusChoices
        from back.apps.language_model.ray_deployments import launch_rag_deployment

        if not os.environ.get('DEBUG') or os.environ.get('RUN_MAIN'):  # only start ray on the main thread
            # raise error if we are in local storage mode and we are trying to use a remote ray cluster
            if settings.LOCAL_STORAGE == "local" and settings.REMOTE_RAY_CLUSTER_ADDRESS_HEAD:
                raise ValueError("Cannot use a remote ray cluster with local storage mode, please set STORAGES_MODE to s3 or do")

            # initialize_or_check_ray()

            # ray_context = ray.init(address='auto', ignore_reinit_error=True)
            # ray_context.__exit__ = lambda *args, **kwargs: None
            # print(f'Result: {type(ray_context)}')

            RAGConfig = self.get_model("RAGConfig")

            # with connect_to_ray_cluster():
            # Now we launch the deployment of the RAGs
            for rag_config in RAGConfig.enabled_objects.all():
                if rag_config.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
                    task_name = f"launch_rag_deployment_{rag_config.name}"
                    logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                    launch_rag_deployment.options(name=task_name).remote(rag_config.id)


