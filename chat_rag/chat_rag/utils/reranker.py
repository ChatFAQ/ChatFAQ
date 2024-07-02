from typing import Any, Dict, List

from sentence_transformers import CrossEncoder

models_dict = {
    'en': 'mixedbread-ai/mxbai-rerank-base-v1', # 'cross-encoder/ms-marco-MiniLM-L-12-v2' for little bit better performance
    'multilingual': 'nreimers/mmarco-mMiniLMv2-L6-H384-v1', # 'nreimers/mmarco-mMiniLMv2-L12-H384-v1' for better performance but slower
}


class ReRanker:
    def __init__(self, lang: str = 'en', model_name: str = None, device: str ='cuda') -> None:
        """
        Class to rerank the retrieved contexts using a cross-encoder.
        It also filters out low confidence contexts.
        """
        lang = lang if lang in models_dict else 'multilingual' # default to multilingual model if language not supported
        model_name = model_name if model_name is not None else models_dict[lang]
        self.model = CrossEncoder(model_name, device=device)

    def __call__(self, query: str, contexts: List[Dict[str, Any]], batch_size: int = 32, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Rerank the retrieved contexts using a cross-encoder.
        Parameters
        ----------
        query: str
            The user message.
        contexts: List[Dict[str, Any]]
            List of retrieved contexts.
        Returns
        -------
        List[Dict[str, Any]]
            List of reranked contexts.
        """
        docs = [context['content'] for context in contexts]
        results = self.model.rank(query, docs, return_documents=False, batch_size=batch_size)

        reranked_contexts = []
        for result in results:
            if result['score'] > threshold:
                reranked_context = contexts[result['corpus_id']]
                reranked_context['score'] = result['score']
                reranked_contexts.append(reranked_context)

        return reranked_contexts

