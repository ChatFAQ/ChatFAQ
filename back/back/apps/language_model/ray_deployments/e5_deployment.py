import asyncio
import os
from typing import List
from urllib.parse import urljoin

from aiohttp import ClientSession
import ray
from ray import serve


@serve.deployment(
    name="retriever_deployment",
    ray_actor_options={
            "num_cpus": 1,
            "resources": {
                "ai_components": 1,
            }
        }
)
class E5Deployment:
    """
    Ray Serve Deployment class for serving the embedding and reranker retriever models in a Ray cluster.
    """

    def __init__(self, model_name, use_cpu, retriever_id, lang='en'):
        from chat_rag.embedding_models import E5Model
        from chat_rag.utils.reranker import ReRanker

        hf_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.token = os.environ.get('BACKEND_TOKEN')
        self.retrieve_endpoint = urljoin(os.environ.get('BACKEND_HOST'), f"/back/api/language-model/retriever-configs/{retriever_id}/retrieve/")

        self.model = E5Model(model_name=model_name, use_cpu=use_cpu, huggingface_key=hf_key)
        self.reranker = ReRanker(lang=lang, device='cpu' if use_cpu else 'cuda')

        print(f"RetrieverDeployment initialized with model_name={model_name}, use_cpu={use_cpu}")

    @serve.batch(max_batch_size=5, batch_wait_timeout_s=0.2)
    async def batch_handler(self, queries: List[str], top_ks: List[int]):
        """
        Batch handler for the retriever model. This method is called by Ray Serve when a batch of requests is received.
        It creates the query embeddings, sends them to a pgvector backend endpoint for retrieval asynchronously and returns the results.
        """
        embeddings = self.model.build_embeddings(queries, prefix='query: ')

        async with ClientSession() as session:
            tasks = []
            headers = {'Authorization': f'Token {self.token}'}

            for i, query_embedding in enumerate(embeddings):
                query_embedding = query_embedding.tolist()
                data = {
                    'query_embeddings': [query_embedding],
                    'top_k': top_ks[i]
                }
                task = self.post_request(session, data, headers)
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

            reranked_results = self.reranker(query, results, threshold=0.5)
            for result in reranked_results:
                result['score'] = result['score'].item() # convert scores from np.float32 to float
            results_reranked.append(reranked_results)

        return results_reranked

    async def post_request(self, session, json, headers):
        async with session.post(self.retrieve_endpoint, json=json, headers=headers) as response:
            return await response.json()

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, query: str, top_k: int):
        return await self.batch_handler(query, top_k)


@ray.remote(num_cpus=0.1, resources={"tasks": 1})
def launch_e5_deployment(retriever_deploy_name, model_name, use_cpu, retriever_id, lang, num_replicas):
    print(f"Launching E5 deployment with name: {retriever_deploy_name}")
    retriever_app = E5Deployment.options(
            name=retriever_deploy_name,
            num_replicas=num_replicas
    ).bind(model_name, use_cpu, retriever_id, lang)

    serve.run(retriever_app, name=retriever_deploy_name, route_prefix=None)
    print(f"Launched E5 deployment with name: {retriever_deploy_name}")
