import os
from typing import List

import ray
from django.conf import settings
from ray import serve
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy

from back.apps.language_model.tasks import read_s3_index


@serve.deployment(
    name="colbert_deployment",
    ray_actor_options={
        "num_cpus": 1,
        "resources": {
            "rags": 1,
        },
    },
)
class ColBERTDeployment:
    """
    ColBERTDeployment class for serving the a ColBERT retriever in a Ray Serve deployment in a Ray cluster.
    """

    def __init__(self, index_path, storages_mode):
        from ragatouille import RAGPretrainedModel

        from chat_rag.utils.reference_checker import clean_relevant_references


        self.clean_relevant_references = clean_relevant_references

        print(f"Initializing ColBERTDeployment with index_path={index_path} and storages_mode={storages_mode}")

        if 's3://' in index_path:
            # Schedule the reading of the index on the same node as the deployment
            node_id = ray.get_runtime_context().get_node_id()
            print(f"Node ID: {node_id}")
            node_scheduling_strategy = NodeAffinitySchedulingStrategy(
                node_id=node_id, soft=False
            )
            index_path_ref = read_s3_index.options(scheduling_strategy=node_scheduling_strategy).remote(index_path, storages_mode)
            index_path = ray.get(index_path_ref)
            print(f"Downloaded index from S3 to {index_path}")
        else:
            index_root, index_name = os.path.split(index_path)
            index_path = os.path.join(index_root, 'colbert', 'indexes', index_name)
            print(f'Reading index locally from {index_path}')

        self.retriever = RAGPretrainedModel.from_index(index_path)

        # Test query for loading the searcher for the first time
        self.retriever.search("test query", k=1)
        print(f"ColBERTDeployment initialized with index_path={index_path}")

    @serve.batch(max_batch_size=5, batch_wait_timeout_s=0.2)
    async def batch_handler(self, queries: List[str], top_ks: List[int]):
        """
        Batch handler for the retriever model. This method is called by Ray Serve when a batch of requests is received.
        It creates the query embeddings, sends them to a pgvector backend endpoint for retrieval asynchronously and returns the results.
        """

        queries_results = self.retriever.search(queries, k=max(top_ks))

        # For normalizing the scores
        query_maxlen = self.retriever.model.model_index.searcher.config.query_maxlen

        # If only one query was passed, the result is not a list
        queries_results = [queries_results] if len(queries) == 1 else queries_results

        results = []
        for query_results, top_k in zip(queries_results, top_ks):
            for result in query_results:
                result["score"] = result["score"] / query_maxlen

            # Filter out results not relevant to the query
            query_results = self.clean_relevant_references(query_results)

            # only keep k_item_id, content and similarity
            query_results = [
                {
                    "k_item_id": int(result["document_id"]),
                    "similarity": result["score"],
                    "content": result["content"],
                }
                for result in query_results
            ]

            results.append(query_results[:top_k])

        return results

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, query: str, top_k: int):
        return await self.batch_handler(query, top_k)


def construct_index_path(index_path: str):
    """
    Construct the index path based on the STORAGES_MODE environment variable.
    """

    if settings.LOCAL_STORAGE:
            return os.path.join("back", index_path)
    else:
        bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")
        return f"s3://{bucket_name}/{index_path}"

@ray.remote(num_cpus=0.1, resources={"tasks": 1})
def launch_colbert_deployment(retriever_deploy_name, index_path, num_replicas):
    print(f"Launching ColBERT deployment with name: {retriever_deploy_name} and index_path: {index_path}")

    storages_mode = settings.STORAGES_MODE

    index_path = construct_index_path(index_path)
    print(f"Index path: {index_path}")
    retriever_app = ColBERTDeployment.options(
        name=retriever_deploy_name, 
        num_replicas=num_replicas
    ).bind(index_path, storages_mode)
    
    serve.run(retriever_app, name=retriever_deploy_name, route_prefix=None)
    print(f"Launched ColBERT deployment with name: {retriever_deploy_name}")
