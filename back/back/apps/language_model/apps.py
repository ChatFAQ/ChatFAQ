import os

from django.apps import AppConfig

from back.utils import is_migrating, is_celery_worker, is_scraping

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
        import ray


        RAGConfig = self.get_model("RAGConfig")

        if not ray.is_initialized() and os.environ.get('RUN_MAIN'): # only start ray on the main thread
            RAY_ADRESS = os.environ.get("RAY_ADDRESS")
            
            # Connect to a ray cluster as a client
            if RAY_ADRESS:
                logger.info(f"Connecting to Ray at {RAY_ADRESS}")
                ray.init(address=RAY_ADRESS, namespace="back-end")
                
            else: # Very unstable, only for local development
                logger.info("Starting Ray locally...")
                # These are the resources for the ray cluster, 'rags' for launching RAGs and 'tasks' for launching tasks
                # these resources are used to specify the nodes in the ray cluster where ray will run the tasks and rags
                # so here they are specified only for compatibility with the ray cluster
                # The actual resources for running these are limited by the number of CPUs and GPUs available on the machine
                # The CPUs and GPUs are automatically detected by ray.
                resources = {
                    "rags": 100,
                    "tasks": 100,
                }
                # init a custom ray cluster
                result = ray.init(
                    ignore_reinit_error=True,
                    resources=resources,
                    include_dashboard=True,
                    dashboard_port=8265,
                    namespace="back-end"
                )
                # check that the python package chat-rag is installed
                try:
                    import chat_rag
                except ImportError:
                    logger.error("chat-rag package not found, please install it to use a local ray cluster")
                    return
            
            logger.info("Available resources:", ray.available_resources())

            # TODO: Not sure about this solution, I need to launch them at start but it's not recommended to interact with the database in the ready method
            # TODO: Maybe make this a django command 

            # Now we launch the deployment of the RAGs
            for rag_config in RAGConfig.enabled_objects.all():
                if rag_config.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
                    logger.info(f"Launching RAG deployment for {rag_config.name}")
                    launch_rag_deployment_task.delay(rag_config.id)

