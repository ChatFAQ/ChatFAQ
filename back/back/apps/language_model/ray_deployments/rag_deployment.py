import json

import ray
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.config import HTTPOptions, ProxyLocation

from starlette.responses import StreamingResponse
from starlette.requests import Request

from back.apps.language_model.models.enums import (
    DeviceChoices,
    RetrieverTypeChoices,
)
from .e5_deployment import launch_e5
from .colbert_deployment import launch_colbert
from logging import getLogger

logger = getLogger(__name__)


@serve.deployment(
    name="rag_orchestrator",
    ray_actor_options={
            "num_cpus": 0.2,
            "resources": {
                "rags": 1,
            }
        }
)
class RAGDeployment:

    class RetrieverHandleClient:
        """Wrapper around the retriever handle to make it compatible with the RAG interface."""
        def __init__(self, handle: DeploymentHandle):
            self.handle = handle
            print("RetrieverHandleClient created")

        async def retrieve(self, message: str, top_k: int):
            print(f"Retrieving for message: {message}")
            result = await self.handle.remote(message, top_k)
            print(f"Results retrieved: {result}")
            return result

    def __init__(self, retriever_handle: DeploymentHandle, llm_name: str, llm_type: str):

        from chat_rag import AsyncRAG
        from chat_rag.llms import (
            AsyncClaudeChatModel,
            AsyncMistralChatModel,
            AsyncOpenAIChatModel,
            AsyncVLLMModel,
        )

        LLM_CLASSES = {
            "claude": AsyncClaudeChatModel,
            "mistral": AsyncMistralChatModel,
            "openai": AsyncOpenAIChatModel,
            "vllm": AsyncVLLMModel,
            "together": AsyncOpenAIChatModel,
        }

        retriever = self.RetrieverHandleClient(retriever_handle)

        # For Together model, we need to set the base_url
        base_url = None
        if llm_type == "together":
            base_url="https://api.together.xyz/v1"

        llm_model = LLM_CLASSES[llm_type](llm_name, base_url=base_url)
        self.rag = AsyncRAG(retriever=retriever, llm_model=llm_model)
        print("RAGDeployment created")

    async def gen_response(self, messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context=False):
        print(f"Generating response for messages: {messages}")
        context_sent = False
        # async for response_dict in self.rag.stream(messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context=only_context):
        async for response_dict in self.rag.stream(messages, prev_contents, prompt_structure_dict, generation_config_dict):
            # Send the context only once
            if not context_sent:
                yield_dict = response_dict
                context_sent = True
            else:
                yield_dict = {"res": response_dict["res"]}
            response_str = json.dumps(yield_dict)
            yield response_str

    def __call__(self, messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context):
        return self.gen_response(messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context)


def launch_rag(rag_deploy_name, retriever_handle, llm_name, llm_type, num_replicas=1):

    print(f'Got retriever handle: {retriever_handle}')
    print(f'Launching RAG deployment with name: {rag_deploy_name}')
    rag_handle = RAGDeployment.options(
        num_replicas=num_replicas,
    ).bind(retriever_handle, llm_name, llm_type)

    print(f'Launched RAG deployment with name: {rag_deploy_name}')
    route_prefix = f'/rag/{rag_deploy_name}'
    serve.run(rag_handle, route_prefix=route_prefix, name=rag_deploy_name).options(stream=True)
    print(f'Launched all deployments')


@ray.remote(num_cpus=0.2, resources={"tasks": 1})
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


@ray.remote(num_cpus=0.5, resources={"tasks": 1})
def launch_rag_deployment(rag_config_id):
    """
    Launch the RAG deployment using Ray Serve.
    """
    from django.conf import settings
    from back.apps.language_model.models import RAGConfig

    rag_config = RAGConfig.objects.get(pk=rag_config_id)
    rag_deploy_name = rag_config.get_deploy_name()
    num_replicas = rag_config.num_replicas

    # delete the deployment if it already exists
    task_name = f'delete_rag_deployment_{rag_deploy_name}'
    print(f"Submitting the {task_name} task to the Ray cluster...")
    # Need to wait for the task to finish before launching the new deployment
    ray.get(delete_rag_deployment.options(name=task_name).remote(rag_deploy_name))

    if not serve.status().applications:
        serve.start(detached=True, proxy_location=ProxyLocation(ProxyLocation.Disabled))

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
    launch_rag(rag_deploy_name, retriever_handle, llm_name, llm_type, num_replicas)
