import os
import asyncio
from typing import List
from aiohttp import ClientSession
from ray import serve
from fastapi import Request
from chat_rag.inf_retrieval.embedding_models import E5Model
from chat_rag.inf_retrieval.cross_encoder import ReRanker


@serve.deployment(
    name="retriever_deployment",
    ray_actor_options={"resources": {"rags": 1}},
)
class RetrieverDeployment:
    """
    RetrieverDeployment class for serving the retriever model in a Ray Serve deployment in a Ray cluster.
    """

    def __init__(self, model_name, use_cpu, lang='en'):
        hf_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.backend_url = os.environ.get('BACKEND_URL')
        self.token = os.environ.get('BACKEND_TOKEN')

        self.model = E5Model(model_name=model_name, use_cpu=use_cpu, huggingface_key=hf_key)
        self.reranker = ReRanker(lang=lang, device='cpu' if use_cpu else 'cuda')

        print(f"RetrieverDeployment initialized with model_name={model_name}, use_cpu={use_cpu}")

    @serve.batch(max_batch_size=5, batch_wait_timeout_s=0.2)
    async def batch_handler(self, requests_list: List[Request]):
        """
        Batch handler for the retriever model. This method is called by Ray Serve when a batch of requests is received.
        It creates the query embeddings, sends them to a pgvector backend endpoint for retrieval asynchronously and returns the results.
        """
        queries = []
        top_ks = []
        thresholds = []
        rag_config_ids = []

        for r in requests_list:
            data = await r.json()
            queries.append(data['query'])
            top_ks.append(data['top_k'])
            rag_config_ids.append(data['rag_config_id'])
            if 'threshold' in data:
                thresholds.append(data['threshold'])
            else:
                thresholds.append(0.0)

        embeddings = self.model.build_embeddings(queries, prefix='query: ')

        async with ClientSession() as session:
            tasks = []
            headers = {'Authorization': f'Token {self.token}'}

            for i, query_embedding in enumerate(embeddings):
                query_embedding = query_embedding.tolist()
                data = {
                    'query_embeddings': [query_embedding],
                    'threshold': thresholds[i],
                    'top_k': top_ks[i]
                }
                retrieve_endpoint = f"{self.backend_url}/api/language-model/rag-configs/{rag_config_ids[i]}/retrieve/"
                task = self.post_request(session, retrieve_endpoint, data, headers)
                tasks.append(task)

            results_list = await asyncio.gather(*tasks)

        results_reranked = self.rerank(queries, results_list)
        return results_reranked

    def rerank(self, queries, results_list):
        results_reranked = []
        for query, results in zip(queries, results_list):
            if not results:
                results_reranked.append([])
                continue

            reranked_results = self.reranker(query, results)
            results_reranked.append(reranked_results)

        return results_reranked

    async def post_request(self, session, url, json, headers):
        async with session.post(url, json=json, headers=headers) as response:
            return await response.json()

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, request: Request):
        return await self.batch_handler(request)