from django.apps import AppConfig
from back.utils import is_server_process
from logging import getLogger
from ray import serve
from ray.serve.config import ProxyLocation


logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"
    ray_context = None

    def ready(self):
        if not is_server_process():
            return
        from back.apps.language_model.signals import on_rag_config_change  # noqa
        from back.apps.language_model.models.enums import IndexStatusChoices
        from back.apps.language_model.ray_deployments import launch_rag_deployment

        RAGConfig = self.get_model("RAGConfig")

        if not serve.status().applications:
            serve.start(detached=True, proxy_location=ProxyLocation(ProxyLocation.Disabled))

        # Now we launch the deployment of the RAGs
        for rag_config in RAGConfig.enabled_objects.all():
            if rag_config.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
                task_name = f"launch_rag_deployment_{rag_config.name}"
                logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                launch_rag_deployment.options(name=task_name).remote(rag_config.id)


