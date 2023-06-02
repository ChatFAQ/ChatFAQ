from typing import List

from transformers import T5Tokenizer


# Refer to https://github.com/google-research/FLAN/blob/main/flan/templates.py for prompts templates FOR FLAN T5
# https://github.com/google-research/FLAN/blob/main/flan/baseline_templates.py

PROMPTS = {
    'en': 'Context: {context}\nQuestion: {question}. Whats the answer?"',
    'fr': 'Contexte: {context}\nQuestion: {question}. Quelle est la réponse?"',
    'es': 'Contexto: {context}\nPregunta: {question}. ¿Cuál es la respuesta?"',
    # ALTERNATIVE PROMPTS
    'en1': '{context}\n\n{question}',
    'en2': 'Context: {context}\nQuestion: {question}\n\nAnswer:', # Falls very much on responding with a), b) 1. 2. etc.
    'en3': 'Context: {context}\nQuestion: {question}. Whats the answer?"',
    'en4': '{context}\n\nAnswer this question \"{question}\" by extracting the answer from the text above.', # Dangerous because it extract the literal answer from the text
}


class PromptGenerator:
    '''Class to generate the prompt for the model.'''

    def __init__(self, model: str = 'T5'):
        """
        Initialize the prompt generator.
        Parameters
        ----------
        model : str, optional
            The model to use, by default 'T5'
        """
        if model == 'T5':
            self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-xl")
            self.create_prompt = self.create_prompt_t5
        else:
            raise ValueError('Model not supported, use "T5"')

    def create_prompt_t5(self, query: str, contexts: List[str], lang: str = 'en', max_length: int = 512):
        """
        Create the prompt for the T5 model.
        Parameters
        ----------
        query : str
            The query to answer.
        contexts : list
            The context to use.
        lang : str, optional
            The language of the prompt, by default 'en'
        max_length : int, optional
            The maximum length of the prompt, by default 512
        Returns
        -------
        str
            The prompt to use.
        """

        if lang not in PROMPTS:
            raise ValueError(f"Language {lang} not supported, use one of {list(PROMPTS.keys())}")

        # augment prompt until 512 tokens
        for n_context in range(1, len(contexts) + 1):
            prompt = PROMPTS[lang].format(context='\n'.join(contexts[:n_context]), question=query)

            if len(self.tokenizer.encode(prompt)) > max_length: # until max_length

                if n_context == 1: # If the first context is too long
                    # truncate context if it is too long
                    max__tokens_context_length = max_length - len(self.tokenizer.encode(PROMPTS[lang].format(context='', question=query))) # Get the max length of the context
                    context_tokens = self.tokenizer.encode(contexts[0], max_length=max__tokens_context_length) # Encode the context and truncate it
                    prompt = PROMPTS[lang].format(context=self.tokenizer.decode(context_tokens), question=query) # Decode the context and add it to the prompt
                    return prompt

                return PROMPTS[lang].format(context='\n'.join(contexts[:n_context-1]), question=query) # Return the prompt with the latest contexts that fit in the max_length

        return prompt
