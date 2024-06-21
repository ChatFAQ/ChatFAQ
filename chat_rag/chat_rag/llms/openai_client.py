import os
from typing import Dict, List

from instructor import Mode, handle_response_model
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
            (
                os.environ.get("TOGETHER_API_KEY")
                if base_url
                else os.environ.get("OPENAI_API_KEY")
            )
            if api_key is None
            else api_key
        )

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.llm_name = llm_name

    def _format_tools(self, tools: List[BaseModel], tool_choice: str = None):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        self._check_tool_choice(tools, tool_choice)

        tools_formatted = []
        for tool in tools:
            _, tool_formatted = handle_response_model(tool, mode=Mode.TOOLS)
            tools_formatted.append(tool_formatted["tools"][0])

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool.model_json_schema()['title'] for tool in tools]:
            tool_choice = {
                "type": "function",
                "function": {
                    "name": tool_choice,
                },
            }
        return tools_formatted, tool_choice

    def _extract_tool_info(self, message) -> List[Dict]:
        """
        Format the tool information from the anthropic response to a standard format.
        """
        tools = []
        for tool in message.tool_calls:
            tools.append(
                {
                    "id": tool.id,
                    "name": tool.function.name,
                    "args": tool.function.arguments,
                }
            )

        return tools

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
        tools: List[BaseModel] = None,
        tool_choice: str = None,
    ) -> str | List:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str | List
            The generated text or a list of tool calls.
        """
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        message = response.choices[0].message
        if response.choices[0].finish_reason == "tool_calls":
            return self._extract_tool_info(message)

        return message.content

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[BaseModel] = None,
        tool_choice: str = None,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str | List
            The generated text or a list of tool calls.
        """
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        message = response.choices[0].message
        if message.tool_calls:
            return self._extract_tool_info(message)

        return message.content
