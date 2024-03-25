import os
import asyncio
from typing import List
from aiohttp import ClientSession
from ray import serve
from fastapi import Request
from chat_rag.inf_retrieval.embedding_models import E5Model


@serve.deployment(
    name="retriever_deployment",
    ray_actor_options={"resources": {"rags": 1}},
)
class RetrieverDeployment:
    """
    RetrieverDeployment class for serving the retriever model in a Ray Serve deployment in a Ray cluster.
    TODO: Add reranker model to the deployment.
    """
    def __init__(self, model_name, use_cpu, rag_config_id):
        hf_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.model = E5Model(model_name=model_name, use_cpu=use_cpu, huggingface_key=hf_key)
        self.retrieve_endpoint = os.environ.get('BACKEND_URL') + f'/api/language-model/rag-configs/{rag_config_id}/retrieve/'
        self.token = os.environ.get('BACKEND_TOKEN')
        print(f"RetrieverDeployment initialized with model_name={model_name}, use_cpu={use_cpu}, retrieve_endpoint={self.retrieve_endpoint}")

    @serve.batch(max_batch_size=5, batch_wait_timeout_s=0.2)
    async def batch_handler(self, requests_list: List[Request]):
        """
        Batch handler for the retriever model. This method is called by Ray Serve when a batch of requests is received.
        It creates the query embeddings, sends them to a pgvector backend endpoint for retrieval asynchronously and returns the results.
        """
        queries = []
        top_ks = []
        thresholds = []
        for r in requests_list:
            data = await r.json()
            queries.append(data['query'])
            top_ks.append(data['top_k'])
            thresholds.append(data['threshold'])
        
        embeddings = self.model.build_embeddings(queries, prefix='query: ')
        
        async with ClientSession() as session:
            tasks = []
            headers = {'Authorization': f'Token {self.token}'}
            print(f"Retrieving {len(embeddings)} queries")
            for i, query_embedding in enumerate(embeddings):
                query_embedding = query_embedding.tolist()
                data = {
                    'query_embeddings': [query_embedding],
                    'threshold': thresholds[i],
                    'top_k': top_ks[i]
                }
                task = self.post_request(session, self.retrieve_endpoint, data, headers)
                tasks.append(task)
            results = await asyncio.gather(*tasks)
        return results

    async def post_request(self, session, url, json, headers):
        async with session.post(url, json=json, headers=headers) as response:
            return await response.json()

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, request: Request):
        return await self.batch_handler(request)