import ray
from ray import serve

from back.apps.language_model.ray_deployments.colbert_deployment import (
    launch_colbert_deployment,
)
from back.apps.language_model.ray_deployments.e5_deployment import launch_e5_deployment
from back.apps.language_model.ray_deployments.llm_deployment import (
    launch_llm_deployment,
)

from back.apps.language_model.ray_deployments.utils import delete_serve_app
