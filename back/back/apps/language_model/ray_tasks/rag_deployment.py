import json

from ray import serve
from starlette.responses import StreamingResponse
from starlette.requests import Request

from chat_rag.inf_retrieval.retrievers import RetrieverClient
from chat_rag.llms import AsyncClaudeChatModel
from chat_rag import AsyncRAG

@serve.deployment(
    name="rag_deployment",
    ray_actor_options={"resources": {"rags": 1}},
)
class RAGDeployment:
    def __init__(self, llm_name):
        retriever = RetrieverClient("http://localhost:8000/retrieve")
        llm_model = AsyncClaudeChatModel(llm_name)
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