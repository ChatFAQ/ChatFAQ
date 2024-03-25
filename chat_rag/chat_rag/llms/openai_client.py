import os
from typing import Dict, List

from openai import AsyncOpenAI, OpenAI

from chat_rag.llms import RAGLLM


class OpenAIChatModel(RAGLLM):
    def __init__(
        self,
        llm_name: str,
        **kwargs,
    ):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.llm_name = llm_name

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
            The tag to indicate the end of the role (system role, user role, assistant role).
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )

        final_messages = [{'role': 'system', 'content': system_prompt}] + messages

        return final_messages

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

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        response = self.client.chat.completions.create(model=self.llm_name,
        messages=messages,
        max_tokens=generation_config_dict["max_new_tokens"],
        temperature=generation_config_dict["temperature"],
        top_p=generation_config_dict["top_p"],
        presence_penalty=generation_config_dict["repetition_penalty"],
        seed=generation_config_dict["seed"],
        n=1,
        stream=False)
        return response.choices[0].message.content

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
        Generate text from a prompt using the model in streaming mode.
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

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        print(messages)

        response = self.client.chat.completions.create(model=self.llm_name,
        messages=messages,
        max_tokens=generation_config_dict["max_new_tokens"],
        temperature=generation_config_dict["temperature"],
        top_p=generation_config_dict["top_p"],
        presence_penalty=generation_config_dict["repetition_penalty"],
        seed=generation_config_dict["seed"],
        n=1,
        stream=True)
        for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                return
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content # return the delta text message


class AsyncOpenAIChatModel(RAGLLM):
    def __init__(
        self,
        llm_name: str,
        **kwargs,
    ):
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.llm_name = llm_name

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
            The tag to indicate the end of the role (system role, user role, assistant role).
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )

        final_messages = [{'role': 'system', 'content': system_prompt}] + messages

        return final_messages

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

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        response = await self.client.chat.completions.create(model=self.llm_name,
        messages=messages,
        max_tokens=generation_config_dict["max_new_tokens"],
        temperature=generation_config_dict["temperature"],
        top_p=generation_config_dict["top_p"],
        presence_penalty=generation_config_dict["repetition_penalty"],
        seed=generation_config_dict["seed"],
        n=1,
        stream=False)
        return response.choices[0].message.content
    
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
        Generate text from a prompt using the model in streaming mode.
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

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        print(messages)

        response = await self.client.chat.completions.create(model=self.llm_name,
        messages=messages,
        max_tokens=generation_config_dict["max_new_tokens"],
        temperature=generation_config_dict["temperature"],
        top_p=generation_config_dict["top_p"],
        presence_penalty=generation_config_dict["repetition_penalty"],
        seed=generation_config_dict["seed"],
        n=1,
        stream=True)
        async for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                return
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content