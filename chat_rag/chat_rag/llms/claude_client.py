from typing import List, Dict
import os

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from chat_rag.llms import RAGLLM, CONTEXT_PREFIX


class ClaudeChatModel(RAGLLM):
    def __init__(self, llm_name, **kwargs) -> None:
        self.llm_name = llm_name
        self.anthropic = Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"],
        )

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prefix: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
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
        Returns
        -------
        list
            The formatted prompt.
        """
        prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )

        for message in messages:
            if message['role'] == 'user':
                prompt += f"{HUMAN_PROMPT} {message['content']}{AI_PROMPT}"
            elif message['role'] == 'assistant':
                prompt += " " + message['content']

        return prompt

    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        Returns
        -------
        str
            The generated text.
        """

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        completion = self.anthropic.completions.create(
            model=self.llm_name,
            max_tokens_to_sample=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
            prompt=prompt,
        )

        return completion.completion
    
    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        Returns
        -------
        str
            The generated text.
        """

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        stream = self.anthropic.completions.create(
            model=self.llm_name,
            max_tokens_to_sample=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
            prompt=prompt,
            stream=True,
        )

        for completion in stream:
            yield completion.completion

        

