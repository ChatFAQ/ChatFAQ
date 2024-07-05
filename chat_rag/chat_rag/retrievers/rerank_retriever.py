from typing import List
from logging import getLogger

from chat_rag.utils.reranker import ReRanker


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
        batch_size: int = 32,
    ):
        contexts_retrieved = self.retriever.retrieve(queries, top_k=top_k)  # retrieve contexts
        contexts_ranked = []
        for query, contexts in zip(queries, contexts_retrieved):
            query_contexts = self.reranker(query, contexts, batch_size=batch_size)  # rerank and filter contexts
            # convert scores from np.float32 to float
            for context in query_contexts:
                context["score"] = context["score"].item()
            contexts_ranked.append(query_contexts)
        return contexts_ranked