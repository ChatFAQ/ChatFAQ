from typing import List, Dict, Optional
import os

from transformers import AutoTokenizer, AutoConfig


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

        self.has_chat_template = self.tokenizer.chat_template is not None
        print(f"Model max length: {self.model_max_length}")


    def format_system_prompt(
            self,
            contexts: List[str],
            system_prefix: str,
            n_contexts_to_use: int = 3,
            lang: str = "en",
            **kwargs,
        ) -> str:
        """
        Formats the system prompt to be used by the model.
        """
        if len(contexts) > 0:
            system_prompt = f"{system_prefix}\n{CONTEXT_PREFIX[lang]}\n"

            for ndx, context in enumerate(contexts):
                system_prompt += f"- {context}"

                if ndx < len(contexts[:n_contexts_to_use]) - 1: # no newline on last context
                    system_prompt += "\n"

            return system_prompt
        else:
            return system_prefix + f"\n{CONTEXT_PREFIX[lang]}\n{NO_CONTEXT_SUFFIX[lang]}"


    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prefix: str,
        system_tag: str,
        system_end: str,
        user_tag: str,
        user_end: str,
        assistant_tag: str,
        assistant_end: str,
        n_contexts_to_use: int = 3,
        max_new_tokens: int = 512,
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
        max_new_tokens : int, optional
            The maximum number of new tokens generated, by default 512
        lang : str, optional
            The language of the prompt, by default 'en'
        """

        for n_contexts in range(n_contexts_to_use, 0, -1):

            system_prompt = self.format_system_prompt(
                contexts, system_prefix, n_contexts, lang
            )

            if self.has_chat_template:
                messages.insert(0, {"role": "system", "content": system_prompt})
                prompt = self.tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    tokenize=False,
                )
            else:
                if (system_tag == "" or system_tag is None):  # To avoid adding the role_end tag if there is no system prefix
                    prompt = f"{system_prompt}\n"
                else:
                    prompt = f"{system_tag}{system_prompt}{system_end}"

                for message in messages:
                    if message['role'] == 'user':
                        prompt += f"{user_tag}{message['content']}{user_end}{assistant_tag}"
                    elif message['role'] == 'assistant':
                        prompt += f"{message['content']}{assistant_end}"

            # get number of tokens
            num_tokens = len(self.tokenizer.tokenize(prompt))

            if num_tokens < self.model_max_length:
                return prompt

        raise Exception(
            "Prompt is too long for the model, please try to reduce the size of the contents"
        )

    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: Dict,
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
        prompt_structure_dict: Dict,
        generation_config_dict: Dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Optional[str | List[str]]:
        pass
