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
        from back.apps.language_model.signals import on_retriever_config_change  # noqa
        from back.apps.language_model.models.enums import IndexStatusChoices
        from back.apps.language_model.ray_deployments import (
            launch_llm_deployment,
        )

        RetrieverConfig = self.get_model("RetrieverConfig")
        LLMConfig = self.get_model("LLMConfig")

        if not serve.status().applications:
            serve.start(
                detached=True, proxy_location=ProxyLocation(ProxyLocation.Disabled)
            )

        # Now we launch the deployment of the RAGs
        for retriever_config in RetrieverConfig.enabled_objects.all():
            if retriever_config.get_index_status() in [
                IndexStatusChoices.OUTDATED,
                IndexStatusChoices.UP_TO_DATE,
            ]:
                task_name = f"launch_rag_deployment_{retriever_config.name}"
                logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                retriever_config.trigger_deploy()

        for llm_config in LLMConfig.enabled_objects.all():
            task_name = f"launch_llm_deployment_{llm_config.name}"
            logger.info(f"Submitting the {task_name} task to the Ray cluster...")
            launch_llm_deployment.options(name=task_name).remote(
                llm_config.get_deploy_name(),
                llm_config.llm_type,
                llm_config.llm_name,
                llm_config.base_url,
                llm_config.model_max_length,
                llm_config.num_replicas,
            )
