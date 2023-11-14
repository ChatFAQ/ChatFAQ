from typing import List, Dict, Optional
import os

from transformers import AutoTokenizer, AutoConfig


CONTEXT_PREFIX = {
    "en": "Given the following contexts: ",
    "fr": "Étant donné les contextes suivants: ",
    "es": "Dados los siguientes contextos: ",
}

QUESTION_PREFIX = {
    "en": "Answer the next question: ",
    "fr": "Répondez à la question suivante: ",
    "es": "Responde la siguiente pregunta: ",
}


class RAGLLM:
    def __init__(
        self,
        llm_name: str,
        model_max_length: int = None,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        **kwargs,
    ) -> None:
        
        auth_token = os.environ["HUGGINGFACE_KEY"]

        self.tokenizer = AutoTokenizer.from_pretrained(
            llm_name, trust_remote_code=trust_remote_code_tokenizer, token=auth_token
        )

        if model_max_length is not None:
            self.model_max_length = model_max_length
        else:
            self.config = AutoConfig.from_pretrained(
                llm_name, trust_remote_code=trust_remote_code_model, token=auth_token
            )
            self.model_max_length = (
                self.config.max_position_embeddings
                if self.config.max_position_embeddings is not None
                else self.tokenizer.model_max_length
            )

        print(f"Model max length: {self.model_max_length}")

    def format_prompt(
        self,
        query: str,
        contexts: List[str],
        system_prefix: str,
        system_tag: str,
        system_end: str,
        user_tag: str,
        user_end: str,
        assistant_tag: str,
        assistant_end: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        query : str
            The query to answer.
        contexts : list
            The context to use.
        system_prefix : str
            The prefix to indicate instructions for the LLM.
        system_tag : str
            The tag to indicate the start of the system prefix for the LLM.
        system_end : str
            The tag to indicate the end of the system prefix for the LLM.
        user_tag : str
            The tag to indicate the start of the user input.
        user_end : str
            The tag to indicate the end of the user input.
        assistant_tag : str
            The tag to indicate the start of the assistant output.
        assistant_end : str
            The tag to indicate the end of the assistant output.
            The tag to indicate the end of the role (system role, user role, assistant role).
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """

        for n_contexts in range(n_contexts_to_use, 0, -1):
            contexts_prompt = CONTEXT_PREFIX[lang]
            for context in contexts[:n_contexts]:
                contexts_prompt += f"- {context}\n"

            if (
                system_tag == "" or system_tag is None
            ):  # To avoid adding the role_end tag if there is no system prefix
                prompt = f"{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{user_end}{assistant_tag}"
            else:
                prompt = f"{system_tag}{system_prefix}{system_end}{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{user_end}{assistant_tag}"

            # get number of tokens
            num_tokens = len(self.tokenizer.tokenize(prompt))

            if num_tokens < self.model_max_length:
                print(f"Prompt length: {num_tokens}")
                return prompt

        raise Exception(
            "Prompt is too long for the model, please try to reduce the size of the contents"
        )

    def generate(
        self,
        query,
        contexts,
        prompt_structure_dict: Dict,
        generation_config_dict: Dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Optional[str | List[str]]:
        pass

    def stream(
        self,
        query,
        contexts,
        prompt_structure_dict: Dict,
        generation_config_dict: Dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Optional[str | List[str]]:
        pass
