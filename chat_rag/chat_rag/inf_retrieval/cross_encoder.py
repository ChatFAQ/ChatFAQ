from typing import Any, Dict, List

from sentence_transformers import CrossEncoder

models_dict = {
    'en': 'cross-encoder/ms-marco-MiniLM-L-6-v2', # 'cross-encoder/ms-marco-MiniLM-L-12-v2' for little bit better performance
    'multilingual': 'nreimers/mmarco-mMiniLMv2-L12-H384-v1', 
}


class ReRanker:
    def __init__(self, lang: str = 'en') -> None:
        lang = lang if lang in models_dict else 'multilingual' # default to multilingual model if language not supported
        self.model = CrossEncoder(models_dict[lang], max_length=512, device='cpu')
        self.confidence_threshold = 0.0

    def __call__(self, query: str, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pairs = [(query, context['content']) for context in contexts]
        scores = self.model.predict(pairs)
        print(f"CrossEncoder: {len(scores)} scores")

        # filter out low confidence scores and sort by score
        scores = [(score, context) for score, context in zip(scores, contexts) if score > self.confidence_threshold]
        print(f"CrossEncoder: {len(scores)} contexts left after filtering")

        if len(scores) == 0:
            return []
        
        scores.sort(key=lambda x: x[0], reverse=True)
        return [context for _, context in scores]

