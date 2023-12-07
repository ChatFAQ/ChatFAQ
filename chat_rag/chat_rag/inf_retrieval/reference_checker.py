from logging import getLogger

from transformers import pipeline

logger = getLogger(__name__)

models_dict = {
    'en': 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli', # 'MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli' for little bit better performance
    'es': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
    'fr': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli',
    'multi': 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli', # 'MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli' for a little bit worse performance but faster
}
    

class ReferenceChecker:
    def __init__(self, lang: str = "en"):
        """
        Class to check if we need to retrieve new contexts. We use a zero-shot classifier to check if the message is a some kind of question or instruction, if not we don't need to retrieve new contexts.
        """
        lang = lang if lang in models_dict else 'multi' # default to multilingual model if language not supported

        self.candidate_labels = ['greeting', 'farewell', 'personal check-in', 'small talk', 'question', 'instruction']
        self.reference_checker = pipeline('zero-shot-classification', model=models_dict[lang], device='cuda')
        logger.info(f"Loaded reference checker for language {lang}")


    def check_references(self, message: str) -> bool:
        """
        Check if the message is a question or instruction. If so, we need to retrieve new contexts.
        """
        output = self.reference_checker(message, self.candidate_labels, multi_label=False)
        return output['labels'][0] in self.candidate_labels[-2:] # return True if label is question or instruction