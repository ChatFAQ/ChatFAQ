from typing import List
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