import json
from asgiref.sync import sync_to_async
from typing import List, Dict
import ray
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.config import ProxyLocation

from back.apps.language_model.models.enums import (
    DeviceChoices,
    RetrieverTypeChoices,
)

from .e5_deployment import launch_e5
from .colbert_deployment import launch_colbert
from logging import getLogger
from chat_rag import RAG

logger = getLogger(__name__)


@serve.deployment(
    name="rag_orchestrator",
    ray_actor_options={
        "num_cpus": 0.2,
        "resources": {
            "rags": 1,
        },
    },
)
class RAGDeployment:
    class RetrieverHandleClient:
        """Wrapper around the retriever handle to make it compatible with the RAG interface."""

        def __init__(self, handle: DeploymentHandle):
            self.handle = handle
            print("RetrieverHandleClient created")

        async def retrieve(self, message: List[str], top_k: int) -> List[List[Dict]]:
            print(f"Retrieving for message: {message}")
            result = await self.handle.remote(message[0], top_k)
            print(f"Results retrieved: {result}")
            return [result]

    def __init__(
        self,
        retriever_handle: DeploymentHandle,
        llm_config_id: int,
        lang: str = "en",
    ):
        self.retriever_handle = retriever_handle
        self.llm_config_id = llm_config_id
        self.lang = lang
        self.rag = None

    async def initialize_rag(self):
        """
        Lazy initialization of the RAG object, we cannot initialize it in the constructor because accessing the database is an async operation and the constructor is synchronous.
        """
        if self.rag is None:
            from back.apps.language_model.models import LLMConfig

            retriever = self.RetrieverHandleClient(self.retriever_handle)

            llm_config = await sync_to_async(LLMConfig.objects.get)(
                pk=self.llm_config_id
            )
            llm = llm_config.load_llm()

            self.rag = RAG(retriever=retriever, llm=llm, lang=self.lang)
            print("Rag Orchestrator initialized.")

    async def gen_response(
        self,
        messages,
        prev_contents,
        temperature,
        max_tokens,
        seed,
        n_contexts_to_use,
        only_context=False,
    ):
        print(f"Generating response for messages: {messages}")
        await self.initialize_rag()  # Ensure RAG is initialized

        context_sent = False
        async for response_dict in self.rag.astream(
            messages, prev_contents, temperature, max_tokens, seed, n_contexts_to_use
        ):
            if not context_sent:
                yield_dict = response_dict
                context_sent = True
            else:
                yield_dict = {"res": response_dict["res"]}
            response_str = json.dumps(yield_dict)
            yield response_str

    async def __call__(
        self,
        messages,
        prev_contents,
        temperature,
        max_tokens,
        seed,
        n_contexts_to_use,
        only_context=False,
    ):
        async for response in self.gen_response(
            messages,
            prev_contents,
            temperature,
            max_tokens,
            seed,
            n_contexts_to_use,
            only_context,
        ):
            yield response


def launch_rag(
    rag_deploy_name,
    retriever_handle,
    llm_config_id,
    lang,
    num_replicas=1,
):
    """
    Launch the RAG deployment with the given retriever and LLM handles.
    """
    print(f"Got retriever handle: {retriever_handle}")
    print(f"Launching RAG deployment with name: {rag_deploy_name}")
    rag_handle = RAGDeployment.options(
        num_replicas=num_replicas,
    ).bind(retriever_handle, llm_config_id, lang)

    print(f"Launched RAG deployment with name: {rag_deploy_name}")
    route_prefix = f"/rag/{rag_deploy_name}"
    serve.run(rag_handle, route_prefix=route_prefix, name=rag_deploy_name).options(
        stream=True
    )
    print("Launched all deployments")


@ray.remote(num_cpus=0.2, resources={"tasks": 1})
def delete_rag_deployment(rag_deploy_name):
    """
    Delete the RAG deployment Ray Serve.
    """
    if serve.status().applications:
        serve.delete(rag_deploy_name)
        try:
            serve.get_app_handle(rag_deploy_name)
            # if it doesn't return error it means the deployment is still running
            print(
                f"{rag_deploy_name} could not be deleted, so it doesn't exist or it is still running."
            )
        except Exception:
            print(f"{rag_deploy_name} was deleted successfully")


@ray.remote(num_cpus=0.5, resources={"tasks": 1})
def launch_rag_deployment(rag_config_id):
    """
    Get all the necessary information from the RAGConfig and launch the RAG deployment.
    """
    from back.apps.language_model.models import RAGConfig

    rag_config = RAGConfig.objects.get(pk=rag_config_id)
    rag_deploy_name = rag_config.get_deploy_name()
    num_replicas = rag_config.num_replicas
    lang = rag_config.knowledge_base.get_lang().value

    # delete the deployment if it already exists
    task_name = f"delete_rag_deployment_{rag_deploy_name}"
    print(f"Submitting the {task_name} task to the Ray cluster...")
    # Need to wait for the task to finish before launching the new deployment
    ray.get(delete_rag_deployment.options(name=task_name).remote(rag_deploy_name))

    if not serve.status().applications:
        serve.start(detached=True, proxy_location=ProxyLocation(ProxyLocation.Disabled))

    retriever_type = rag_config.retriever_config.get_retriever_type()
    retriever_deploy_name = f"retriever_{rag_config.retriever_config.name}"

    if retriever_type == RetrieverTypeChoices.E5:
        model_name = rag_config.retriever_config.model_name
        use_cpu = rag_config.retriever_config.get_device() == DeviceChoices.CPU
        retriever_handle = launch_e5(
            retriever_deploy_name, model_name, use_cpu, rag_config_id, lang
        )

    elif retriever_type == RetrieverTypeChoices.COLBERT:
        # For ColBERT we only need the index path as this contains the model name and other necessary information
        retriever_handle = launch_colbert(
            retriever_deploy_name, rag_config.s3_index_path
        )

    else:
        raise ValueError(f"Retriever type: {retriever_type.value} not supported.")

    # LLM Info
    llm_config_id = rag_config.llm_config.pk

    launch_rag(
        rag_deploy_name,
        retriever_handle,
        llm_config_id,
        lang,
        num_replicas,
    )
