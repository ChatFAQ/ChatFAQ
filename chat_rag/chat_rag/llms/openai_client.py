import os
from typing import Dict, List

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from chat_rag.llms import LLM


class OpenAIChatModel(LLM):
    def __init__(
        self,
        llm_name: str= "gpt-4o",
        base_url: str = None,
        **kwargs,
    ):  
        # If provided a base_url, then use the Together API key
        api_key = os.environ.get("TOGETHER_API_KEY") if base_url else os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        contexts: List[str] = None,
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
        system_prompt : str
            The prefix to indicate instructions for the LLM.
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prompt=system_prompt,
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

    def use_tools(messages: List[Dict], tools: List[BaseModel], tool_choice: str = 'any'):
        """
        Use the tools to process the messages.
        Parameters
        ----------
        messages : List[Dict]
            The messages to send to the model.
        tools : List[BaseModel]
            The tools to use.
        tool_choice : str
            The choice of the tool to use. If 'any', then any tool can be used, if you specify a tool name, then only that tool will be used.
        Returns
        -------
        List[Dict]
            The processed messages.
        """
        # check that if tool_choice is not any, then the tool_choice is in the tools
        if tool_choice != 'any':
            tools_names = [tool.__repr_name__() for tool in tools]
            assert tool_choice in tools_names, f"The tool choice {tool_choice} is not in the tools provided. You chose {tool_choice} and the tools are {tools_names}."

        

class AsyncOpenAIChatModel(LLM):
    def __init__(
        self,
        llm_name: str,
        base_url: str = None,
        **kwargs,
    ):
        # If provided a base_url, then use the Together API key
        api_key = os.environ.get("TOGETHER_API_KEY") if base_url else os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prompt: str,
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
        system_prompt : str
            The prefix to indicate instructions for the LLM.
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prompt=system_prompt,
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