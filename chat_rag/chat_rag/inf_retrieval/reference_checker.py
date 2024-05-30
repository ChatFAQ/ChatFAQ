from logging import getLogger
from typing import Any, Dict, List

import numpy as np
from transformers import pipeline

logger = getLogger(__name__)

models_dict = {
    'en': 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli', # 'MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli' for little bit better performance
    'es': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
    'fr': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
    'multi': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli', # 'MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli' for a little bit worse performance but faster
}
    

class ReferenceChecker:
    def __init__(self, lang: str = "en", device: str = 'cuda'):
        """
        Class to check if we need to retrieve new contexts. We use a zero-shot classifier to check if the message is a some kind of question or instruction, if not we don't need to retrieve new contexts.
        """
        lang = lang if lang in models_dict else 'multi' # default to multilingual model if language not supported

        self.candidate_labels = ['greeting', 'farewell', 'personal check-in', 'small talk', "acknowledgments", 'question', 'instruction']
        self.true_labels = ['question', 'instruction']
        self.reference_checker = pipeline('zero-shot-classification', model=models_dict[lang], device=device)
        logger.info(f"Loaded reference checker for language {lang}")


    def check_references(self, message: str) -> bool:
        """
        Check if the message is a question or instruction. If so, we need to retrieve new contexts.
        """
        output = self.reference_checker(message, self.candidate_labels, multi_label=False)
        label = output['labels'][0]
        if label in self.true_labels: # if label is question or instruction, then retrieve
            return True
        
        # For doubful cases, we retrieve new contexts, 
        # e.g. if the label is not question or instruction but the score of one of those is close to the highest score
        highest_score = output['scores'][0]
        for true_label in self.true_labels:
            if (highest_score - output['scores'][output['labels'].index(true_label)]) < 0.1:
                return True

        return False # if not question or instruction, then don't retrieve
    

def clean_relevant_references(sources: List[Dict[str, Any]], min_difference=0.09, min_score=0.3, score_key: str = 'score') -> List[Dict[str, Any]]:
    """
    Find the relevant sources from a list of sources. We use the similarity scores to find the relevant sources. We calculate the standard deviation of the gaps between consecutive sources and return all sources up to the first significant gap.
    Parameters
    ----------
    sources: List[Dict[str, Any]]
        List of sources to find the relevant sources from.
    min_difference: float
        Minimum difference between consecutive sources to be considered a significant gap.
    min_score: float
        Minimum score for a source to be considered relevant.
    Returns
    -------
    List[Dict[str, Any]]
        List of relevant sources.
    """

    # Calculate gaps between consecutive sources
    # print the similarity scores
    gaps = [sources[i][score_key] - sources[i + 1][score_key] for i in range(len(sources) - 1)]

    # Compute standard deviation of the gaps if there are enough gaps
    if len(gaps) > 1:
        std_dev = np.std(gaps)
    else:
        # If there's only one gap or none, return all sources as relevant
        return sources

    # Identify the first significant gap
    for i, gap in enumerate(gaps):
        if gap > std_dev and gap > min_difference:  # A significant gap
            return sources[:i + 1]
        
    final_sources = []
    for source in sources:
        if source[score_key] > min_score:
            final_sources.append(source)

    # If no significant gap found, return all sources
    return final_sources