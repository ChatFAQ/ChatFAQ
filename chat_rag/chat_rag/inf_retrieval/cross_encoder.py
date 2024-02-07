from typing import Any, Dict, List

import torch
from sentence_transformers import CrossEncoder

models_dict = {
    'en': 'cross-encoder/ms-marco-MiniLM-L-6-v2', # 'cross-encoder/ms-marco-MiniLM-L-12-v2' for little bit better performance
    'multilingual': 'nreimers/mmarco-mMiniLMv2-L6-H384-v1', # 'nreimers/mmarco-mMiniLMv2-L12-H384-v1' for better performance but slower
}


class ReRanker:
    def __init__(self, lang: str = 'en', device: str = 'cuda', model_name: str = None) -> None:
        """
        Class to rerank the retrieved contexts using a cross-encoder.
        It also filters out low confidence contexts.
        """
        lang = lang if lang in models_dict else 'multilingual' # default to multilingual model if language not supported
        model_name = model_name if model_name is not None else models_dict[lang]
        self.model = CrossEncoder(model_name, max_length=512, device=device)
        self.confidence_threshold = 0.5
        self.activation_fct = torch.sigmoid
        self.max_query_length = 64 # These cross-encoder are not trained on long queries, so we restrict them down to simple queries of max 64 characters 
        # You can see some of these stats here (https://huggingface.co/datasets/ms_marco)

    def __call__(self, query: str, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        if len(query) > self.max_query_length: # for queries longer than 64 characters, we do not rerank
            return contexts
        
        pairs = [(query, context['content']) for context in contexts]
        scores = self.model.predict(pairs, activation_fct=self.activation_fct)
        print(f"CrossEncoder: {scores} scores")

        # filter out low confidence scores and sort by score
        scores = [(score, context) for score, context in zip(scores, contexts) if score > self.confidence_threshold]
        print(f"CrossEncoder: {len(scores)} contexts left after filtering")

        if len(scores) == 0:
            return []
        
        scores.sort(key=lambda x: x[0], reverse=True)
        return [context for _, context in scores]

