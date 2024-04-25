import json

from ray import serve
from ray.serve.handle import DeploymentHandle
from starlette.responses import StreamingResponse
from starlette.requests import Request



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

        async def retrieve(self, message: str, top_k: int):
            return await self.handle.remote(message, top_k)

    def __init__(self, retriever_handle: DeploymentHandle, llm_name: str, llm_type: str):

        from chat_rag.llms import AsyncClaudeChatModel, AsyncMistralChatModel, AsyncOpenAIChatModel, AsyncVLLMModel
        from chat_rag import AsyncRAG

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

    async def gen_response(self, messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context=False):
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

    async def __call__(self, request: Request) -> StreamingResponse:
        data = await request.json()
        messages = data["messages"]
        prev_contents = data["prev_contents"]
        prompt_structure_dict = data["prompt_structure_dict"]
        generation_config_dict = data["generation_config_dict"]
        only_context = data.get("only_context", False)

        return StreamingResponse(
            self.gen_response(messages, prev_contents, prompt_structure_dict, generation_config_dict, only_context),
            media_type="application/json",
            status_code=200,
        )

def launch_rag(rag_deploy_name, retriever_handle, llm_name, llm_type):

    print(f'Got retriever handle: {retriever_handle}')
    print(f'Launching RAG deployment with name: {rag_deploy_name}')
    rag_handle = RAGDeployment.options(
        num_replicas=2,
    ).bind(retriever_handle, llm_name, llm_type)

    print(f'Launched RAG deployment with name: {rag_deploy_name}')
    route_prefix = f'/rag/{rag_deploy_name}'
    serve.run(rag_handle, route_prefix=route_prefix, name=rag_deploy_name)
    print(f'Launched all deployments')
