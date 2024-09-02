import json
import os
from typing import Dict, List, Union

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from .base_llm import LLM
from .format_tools import Mode, format_tools
from .message import Content, Message, ToolUse, Usage


def map_openai_message(openai_message) -> Message:
    # Map usage
    usage = Usage(
        input_tokens=openai_message.usage.prompt_tokens,
        output_tokens=openai_message.usage.completion_tokens
    )
    content_blocks: List[Content] = []
    for choice in openai_message.choices:
        if choice.message.tool_calls:
            tool_uses = [ToolUse(id=tool_call.id, name=tool_call.function.name, arguments=json.loads(tool_call.function.arguments)) for tool_call in choice.message.tool_calls]
            content_blocks.append(Content(stop_reason=choice.finish_reason, role=choice.message.role, type="tool_use", tool_use=tool_uses))
        else:
            content_blocks.append(Content(text=choice.message.content, stop_reason=choice.finish_reason, role=choice.message.role, type="text"))

    message = Message(
        model=openai_message.model,
        usage=usage,
        content=content_blocks,
        created=openai_message.created
    )

    return message


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
        tools, tool_choice = self._check_tool_choice(tools, tool_choice)

        tools_formatted = format_tools(tools, mode=Mode.TOOLS)

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool['title'] for tool in tools]:
            tool_choice = {
                "type": "function",
                "function": {
                    "name": tool_choice,
                },
            }
        return tools_formatted, tool_choice

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
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        Message
            The generated message.
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

        return map_openai_message(response)

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        Message
            The generated message.
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

        return map_openai_message(response)