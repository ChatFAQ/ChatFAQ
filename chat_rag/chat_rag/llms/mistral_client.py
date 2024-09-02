import os
from typing import Dict, List, Union
import json

from mistralai import Mistral
from pydantic import BaseModel

from .base_llm import LLM
from .message import Message, Usage, Content, ToolUse
from .format_tools import Mode, format_tools


def map_mistral_message(mistral_message):
    usage = Usage(
        input_tokens=mistral_message.usage.prompt_tokens,
        output_tokens=mistral_message.usage.completion_tokens
    )
    content_blocks = []
    for choice in mistral_message.choices:
        if choice.message.tool_calls:
            tool_uses = [ToolUse(id=tool_call.id, name=tool_call.function.name, input=json.loads(tool_call.function.arguments)) for tool_call in choice.message.tool_calls]
            content_blocks.append(Content(stop_reason=choice.finish_reason, role=choice.message.role, type="tool_use", tool_use=tool_uses))
        else:
            content_blocks.append(Content(text=choice.message.content, stop_reason=choice.finish_reason, role=choice.message.role, type="text"))

    message = Message(
        model=mistral_message.model,
        usage=usage,
        content=content_blocks,
        created=mistral_message.created
    )

    return message


class MistralChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "mistral-large-latest",
        **kwargs,
    ):
        self.client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        self.llm_name = llm_name

    def _format_tools(self, tools: List[BaseModel], tool_choice: str = None):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        tools, tool_choice = self._check_tool_choice(tools, tool_choice)

        tools_formatted = format_tools(tools, mode=Mode.TOOLS)

        if tool_choice:
            if tool_choice not in ["required", "auto"]:
                raise ValueError(
                    "Named tool choice is not supported for Mistral, only 'required' or 'auto' is supported."
                )

            tool_choice = (
                "any" if tool_choice == "required" else tool_choice
            )  # map "required" to "any"

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


        for chunk in self.client.chat.stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.data.choices[0].delta.content is not None:
                yield chunk.data.choices[0].delta.content

        return

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


        async for chunk in self.client.chat.stream_async(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.data.choices[0].delta.content is not None:
                yield chunk.data.choices[0].delta.content

        return

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ):
        """
        Generate text from a prompt using a model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        chat_response = self.client.chat.complete(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        return map_mistral_message(chat_response)

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ):
        """
        Generate text from a prompt using a model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """
        
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        chat_response = await self.client.chat.complete_async(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        return map_mistral_message(chat_response)