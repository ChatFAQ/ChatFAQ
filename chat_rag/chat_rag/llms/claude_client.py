import os
from typing import Dict, List

from anthropic import Anthropic, AsyncAnthropic

from chat_rag.llms import CONTEXT_PREFIX, RAGLLM


class ClaudeChatModel(RAGLLM):
    def __init__(self, llm_name, **kwargs) -> None:
        self.llm_name = llm_name
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def format_prompt(
        self,
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
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )

        return system_prompt

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

        system_prompt = self.format_prompt(contexts, **prompt_structure_dict, lang=lang)

        message = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            max_tokens=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
        )

        return message.content[0].text
    
    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ):
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

        system_prompt = self.format_prompt(contexts, **prompt_structure_dict, lang=lang)

        stream = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            max_tokens=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
            stream=True,
        )

        for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text

        
class AsyncClaudeChatModel(RAGLLM):
    def __init__(self, llm_name, **kwargs) -> None:
        self.llm_name = llm_name
        self.client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def format_prompt(
        self,
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
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )

        return system_prompt
    
    async def generate(
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

        system_prompt = self.format_prompt(contexts, **prompt_structure_dict, lang=lang)

        message = await self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            max_tokens=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
        )

        return message.content[0].text
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ):
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

        system_prompt = self.format_prompt(contexts, **prompt_structure_dict, lang=lang)

        stream = await self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            max_tokens=generation_config_dict['max_new_tokens'],
            temperature=generation_config_dict['temperature'],
            top_p=generation_config_dict['top_p'],
            top_k=generation_config_dict['top_k'],
            stream=True,
        )

        async for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text
