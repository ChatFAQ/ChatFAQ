import os
from typing import Dict, List

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from chat_rag.llms import LLM


class OpenAIChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "gpt-4o",
        base_url: str = None,
        api_key: str = None,
        **kwargs,
    ):
        # If provided a base_url, then use the Together API key
        api_key = (
            os.environ.get("TOGETHER_API_KEY")
            if base_url
            else os.environ.get("OPENAI_API_KEY")
        ) if api_key is None else api_key
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.llm_name = llm_name

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                return
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content  # return the delta text message

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                return
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=False,
        )
        return response.choices[0].message.content

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=False,
        )
        return response.choices[0].message.content

    def use_tools(
        messages: List[Dict], tools: List[BaseModel], tool_choice: str = "any"
    ):
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
        if tool_choice != "any":
            tools_names = [tool.__repr_name__() for tool in tools]
            assert (
                tool_choice in tools_names
            ), f"The tool choice {tool_choice} is not in the tools provided. You chose {tool_choice} and the tools are {tools_names}."
