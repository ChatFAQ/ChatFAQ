from typing import List, Dict, Optional

from chat_rag.exceptions import PromptTooLongException
from chat_rag.llms import LLM


CONTEXT_PREFIX = {
    "en": "Information:",
    "fr": "Informations:",
    "es": "Información:",
}

NO_CONTEXT_SUFFIX = {
    "en": "No information provided.",
    "fr": "Aucune information n'a été fournie.",
    "es": "No se proporciona información.",
}


class RAGLLM:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def format_system_prompt(
        self,
        contexts: List[str],
        system_prompt: str,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Formats the system prompt to be used by the model.
        """
        if len(contexts) > 0:
            system_prompt = f"{system_prompt}\n{CONTEXT_PREFIX[lang]}\n"

            for ndx, context in enumerate(contexts):
                system_prompt += f"- {context}"

                if ndx < len(contexts) - 1:  # no newline on last context
                    system_prompt += "\n"

            return system_prompt
        else:
            return (
                system_prompt + f"\n{CONTEXT_PREFIX[lang]}\n{NO_CONTEXT_SUFFIX[lang]}"
            )
        
    def apply_chat_template(self, messages, contexts, system_prompt, lang):
        """
        Applies the chat template to the messages and contexts.
        """
        system_prompt = self.format_system_prompt(
                contexts, system_prompt, lang
            )

        new_messages = messages.copy() # copy the messages to avoid modifying the original list
        new_messages.insert(0, {"role": "system", "content": system_prompt})
        prompt = self.tokenizer.apply_chat_template(
                new_messages,
                add_generation_prompt=True,
                tokenize=False,
            )
        return prompt

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prompt: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. List of pairs (role, content).
        contexts : list
            The context to use.
        system_prompt : str
            The prefix to indicate instructions for the LLM.
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """

        n_messages_to_keep = len(messages)
        n_contexts = n_contexts_to_use if len(contexts) > n_contexts_to_use else len(contexts)

        prompt = self.apply_chat_template(messages, contexts, system_prompt, lang)
        num_tokens = len(self.tokenizer.tokenize(prompt))

        margin = int(self.model_max_length * 0.1)

        while num_tokens > (self.model_max_length -  margin):

            if n_contexts == 1 and n_messages_to_keep > 1:
                n_messages_to_keep -= 1

            n_contexts = n_contexts - 1 if n_contexts > 1 else 1

            # When we reach the minimum number of contexts and messages and the prompt is still too long, we return None
            if n_contexts == 1 and n_messages_to_keep == 1:
                raise PromptTooLongException()

            prompt = self.apply_chat_template(messages[:n_messages_to_keep], contexts[:n_contexts], system_prompt, lang)

            # get number of tokens
            num_tokens = len(self.tokenizer.tokenize(prompt))

        return prompt, (n_contexts, n_messages_to_keep)


    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        generation_config_dict: Dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Optional[str | List[str]]:
        pass

    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        generation_config_dict: Dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Optional[str | List[str]]:
        pass