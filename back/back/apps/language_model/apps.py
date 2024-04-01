import os
from django.apps import AppConfig
from back.utils import is_migrating, is_celery_worker, is_scraping
from back.utils.ray_connection import initialize_or_check_ray
from logging import getLogger


logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        if is_migrating() or is_scraping() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from .signals import on_rag_config_change
        from back.apps.language_model.models.enums import IndexStatusChoices
        from back.apps.language_model.tasks import launch_rag_deployment_task


        if os.environ.get('RUN_MAIN'):  # only start ray on the main thread
            
            initialize_or_check_ray()

            RAGConfig = self.get_model("RAGConfig")

            # Now we launch the deployment of the RAGs
            for rag_config in RAGConfig.enabled_objects.all():
                if rag_config.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
                    logger.info(f"Launching RAG deployment for {rag_config.name}")
                    launch_rag_deployment_task.delay(rag_config.id)


