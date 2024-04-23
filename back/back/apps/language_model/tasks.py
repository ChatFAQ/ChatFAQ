import uuid
from logging import getLogger

import ray
from crochet import setup
from django.apps import apps
from django.conf import settings
from django.db.models import F
from ray import serve
from ray.serve.config import HTTPOptions, ProxyLocation

from back.apps.language_model.models.enums import (
    DeviceChoices,
    RetrieverTypeChoices,
)
from back.apps.language_model.ray_deployments import (
    launch_colbert,
    launch_e5,
    launch_rag,
)
from back.apps.language_model.tasks import (
    test_task as ray_test_task,
)
from back.config.celery import app
from back.utils.celery import is_celery_worker
from back.utils.ray_connection import connect_to_ray_cluster

if is_celery_worker():
    setup()

logger = getLogger(__name__)



def delete_rag_deployment(rag_deploy_name):
    """
    Delete the RAG deployment Ray Serve.
    """
    if serve.status().applications:
        serve.delete(rag_deploy_name)
        try:
            app_handle = serve.get_app_handle(rag_deploy_name)
            # if it doesn't return error it means the deployment is still running
            print(f"{rag_deploy_name} could not be deleted, so it doesn't exist or it is still running.")
        except:
            print(f'{rag_deploy_name} was deleted successfully')

    # When all deployments are deleted, shutdown the serve instance
    if not serve.status().applications:
        serve.shutdown()


@app.task()
def delete_rag_deployment_task(rag_deploy_name):
    with connect_to_ray_cluster(close_serve=True):
        delete_rag_deployment(rag_deploy_name)


def launch_rag_deployment(rag_config_id):
    """
    Launch the RAG deployment using Ray Serve.
    """
    RAGConfig = apps.get_model("language_model", "RAGConfig")

    rag_config = RAGConfig.objects.get(pk=rag_config_id)
    rag_deploy_name = rag_config.get_deploy_name()
        # delete the deployment if it already exists
    delete_rag_deployment(rag_deploy_name)

    if not serve.status().applications:
        http_options = HTTPOptions(host="0.0.0.0", port=settings.RAY_SERVE_PORT)  # Connect to local cluster or to local Ray driver (both by default run in the same addresses)
        proxy_location = ProxyLocation(ProxyLocation.EveryNode)

        serve.start(detached=True, http_options=http_options, proxy_location=proxy_location)

    retriever_type = rag_config.retriever_config.get_retriever_type()
    retriever_deploy_name = f'retriever_{rag_config.retriever_config.name}'

    if retriever_type == RetrieverTypeChoices.E5:
        model_name = rag_config.retriever_config.model_name
        use_cpu = rag_config.retriever_config.get_device() == DeviceChoices.CPU
        lang = rag_config.knowledge_base.get_lang().value
        retriever_handle = launch_e5(retriever_deploy_name, model_name, use_cpu, rag_config_id, lang)

    elif retriever_type == RetrieverTypeChoices.COLBERT:
        retriever_handle = launch_colbert(retriever_deploy_name, rag_config.s3_index_path)

    else:
        raise ValueError(f"Retriever type: {retriever_type.value} not supported.")

    llm_name = rag_config.llm_config.llm_name
    llm_type = rag_config.llm_config.get_llm_type().value
    launch_rag(rag_deploy_name, retriever_handle, llm_name, llm_type)


@app.task()
def launch_rag_deployment_task(rag_config_id):
    with connect_to_ray_cluster(close_serve=True):
        launch_rag_deployment(rag_config_id)




@app.task()
def test_task():
    with connect_to_ray_cluster():
        test_task_ref = ray_test_task.options(name="test_task").remote(str(uuid.uuid4()))
        res_test_task = ray.get(test_task_ref)
        return res_test_task
