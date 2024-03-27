import json

from ray import serve
from ray.serve.handle import DeploymentHandle
from starlette.responses import StreamingResponse
from starlette.requests import Request

from chat_rag.inf_retrieval.retrievers import RetrieverClient
from chat_rag.llms import AsyncClaudeChatModel, AsyncMistralChatModel, AsyncOpenAIChatModel, AsyncVLLMModel
from chat_rag import AsyncRAG


LLM_CLASSES = {
    "claude": AsyncClaudeChatModel,
    "mistral": AsyncMistralChatModel,
    "openai": AsyncOpenAIChatModel,
    "vllm": AsyncVLLMModel,
}


class RetrieverHandleClient:
    """Wrapper around the retriever handle to make it compatible with the RAG interface."""
    def __init__(self, handle: DeploymentHandle):
        self.handle = handle
    
    async def retrieve(self, message: str, top_k: int):
        return await self.handle.remote(message, top_k)
    

@serve.deployment(
    name="rag_deployment",
    ray_actor_options={"resources": {"rags": 1}},
)
class RAGDeployment:
    def __init__(self, retriever_handle: DeploymentHandle, llm_name: str, llm_type: str):
        retriever = RetrieverHandleClient(retriever_handle)
        llm_model = LLM_CLASSES[llm_type](llm_name)
        self.rag = AsyncRAG(retriever=retriever, llm_model=llm_model)

    async def gen_response(self, messages, prev_contents, prompt_structure_dict, generation_config_dict):
        context_sent = False
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

        return StreamingResponse(
            self.gen_response(messages, prev_contents, prompt_structure_dict, generation_config_dict),
            media_type="application/json",
            status_code=200,
        )