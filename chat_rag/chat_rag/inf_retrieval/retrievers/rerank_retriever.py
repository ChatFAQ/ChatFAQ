from typing import List
from logging import getLogger

from chat_rag.inf_retrieval.cross_encoder import ReRanker


logger = getLogger(__name__)


class ReRankRetriever:
    """
    Class for reranking retrieved contexts on top of the retrieval model.
    """
    def __init__(self, retriever, lang, device):
        self.retriever = retriever
        self.reranker = ReRanker(lang=lang, device=device)

    def retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
    ):
        contexts_retrieved = self.retriever.retrieve(queries, top_k=top_k)  # retrieve contexts
        contexts_ranked = []
        for query, contexts in zip(queries, contexts_retrieved):
            query_contexts = self.reranker(query, contexts)  # rerank and filter contexts
            contexts_ranked.append(query_contexts)
        return contexts_ranked
