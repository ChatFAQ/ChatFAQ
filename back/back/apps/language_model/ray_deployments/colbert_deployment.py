from typing import List
from ray import serve
from fastapi import Request

from ragatouille import RAGPretrainedModel

from chat_rag.inf_retrieval.reference_checker import clean_relevant_references


@serve.deployment(
    name="colbert_deployment",
    ray_actor_options={
            "num_cpus": 1,
            "resources": {
                "rags": 1,
            }
        }
)
class ColBERTDeployment:
    """
    ColBERTDeployment class for serving the a ColBERT retriever in a Ray Serve deployment in a Ray cluster.
    """
    def __init__(self, index_path):
        print(f"Initializing ColBERTDeployment")
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
                result["similarity"] = (
                    result["score"] / query_maxlen
                )
            
            # Filter out results not relevant to the query
            query_results = clean_relevant_references(query_results)

            # only keep k_item_id, content and similarity
            query_results = [{"k_item_id": int(result["document_id"]), "similarity": result["similarity"], "content": result["content"]} for result in query_results]

            results.append(query_results[:top_k])

        return results

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, query: str, top_k: int):
        return await self.batch_handler(query, top_k)
    

def launch_colbert(retriever_deploy_name, index_path):
    print(f"Launching ColBERT deployment with name: {retriever_deploy_name}")
    retriever_handle = ColBERTDeployment.options(
            name=retriever_deploy_name,
        ).bind(index_path)
    print(f'Launched ColBERT deployment with name: {retriever_deploy_name}')
    return retriever_handle