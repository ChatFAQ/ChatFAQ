from typing import List
from chat_rag.inf_retrieval.embedding_models.base_model import BaseModel
from pgvector.django import MaxInnerProduct
from back.apps.language_model.models.data import KnowledgeItem
from back.apps.language_model.models.rag_pipeline import RAGConfig


def retrieve_kitems(query_embedding, threshold, top_k, rag_config):
    """
    Returns the context for the given query_embedding.
    Parameters
    ----------
    query_embedding : torch.Tensor, np.ndarray or list
        Query embedding to be used for retrieval.
    threshold : float
        Threshold for filtering the context.
    top_k : int
        Number of context to be returned. If -1, all context are returned.
    rag_config : RAGConfig
        RAGConfig to be used for filtering the KnowledgeItems.
    """
    items_for_query = (
            KnowledgeItem.objects.filter(embedding__rag_config=rag_config)
            .annotate(
                similarity=-MaxInnerProduct("embedding__embedding", query_embedding)
            )
            .filter(similarity__gt=threshold)
            .order_by("-similarity")
        )

    if top_k != -1:
        items_for_query = items_for_query[:top_k]

    query_results = [
        {
            "k_item_id": item.id,
            "content": item.content,
            "similarity": item.similarity,
        }
        for item in items_for_query
    ]
    return query_results


class PGVectorRetriever:
    """Class for retrieving the context for a given query using PGVector"""

    def __init__(self, embedding_model: BaseModel, rag_config: RAGConfig):
        """
        Parameters
        ----------
        embedding_model: BaseModel
            Embedding model to be used for retrieval
        rag_config: RAGConfig
            RAGConfig to be used for filtering the KnowledgeItems
        """
        self.embedding_model = embedding_model
        self.rag_config = rag_config

    def retrieve(self, queries: List[str], top_k: int = 5, threshold: float = None):
        """
        Returns the context for the queries.
        Parameters
        ----------
        queries : List[str]
            List of queries to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.
        threshold : float, optional
            Threshold for filtering the context, by default None.
        """

        queries_embeddings = self.embedding_model.build_embeddings(
            queries, prefix="query: ", disable_progress_bar=True
        )  # specific prefix for e5 models queries

        threshold = threshold if threshold is not None else 0

        results = []
        for query_embedding in queries_embeddings:

            query_results = retrieve_kitems(
                query_embedding, threshold, top_k, self.rag_config
            )
            results.append(query_results)

        return results
