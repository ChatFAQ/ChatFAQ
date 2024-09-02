import os
from typing import Dict, List, Union, Iterator
import json

from anthropic import Anthropic, AsyncAnthropic
from anthropic._types import NOT_GIVEN
from anthropic.types.message import Message as AnthropicMessage
from pydantic import BaseModel

from .base_llm import LLM
from .format_tools import Mode, format_tools
from .message import Content, Message, ToolUse, Usage


def map_anthropic_message(anthropic_message: AnthropicMessage) -> Message:
    # Map usage
    usage = Usage(
        input_tokens=anthropic_message.usage.input_tokens,
        output_tokens=anthropic_message.usage.output_tokens
    )

    # Map content blocks
    content_blocks: List[Content] = []
    for block in anthropic_message.content:
        if block.type == "text":
            content_blocks.append(Content(
                text=block.text,
                type="text",
                stop_reason=anthropic_message.stop_reason,
                role=anthropic_message.role
            ))
        elif block.type == "tool_use":
            tool_use = ToolUse(id=block.id, name=block.name, arguments=block.input)
            content_blocks.append(Content(
                # text="",
                type="tool_use",
                tool_use=[tool_use],
                stop_reason=anthropic_message.stop_reason,
                role=anthropic_message.role
            ))
    # Map the entire message
    message = Message(
        content=content_blocks,
        model=anthropic_message.model,
        usage=usage
    )

    return message


def map_anthropic_stream(stream: Iterator) -> Iterator[Content]:
    """
    Process an Anthropic stream and return a stream of messages. 
    Text is streamed as text_delta.
    The tool use is not streamed, it is accumulated and returned as a single tool use.
    In the last message, the usage is returned.
    """
    tool_use_name = None
    tool_use_id = None
    tool_use_arguments = None
    model = None
    role = None

    for event in stream:
        if event.type == "message_start":
            model = event.message.model
            role = event.message.role
        elif event.type == "content_block_delta" and event.delta.type == "text_delta":
            yield Message(
                model=model,
                role=role,
                content=[Content(type="text_delta", text=event.delta.text, role=role, stop_reason="")]
            )
        elif event.type == "content_block_start" and event.content_block.type == "tool_use":
            tool_use_name = event.content_block.name
            tool_use_id = event.content_block.id
            tool_use_arguments = ""
        elif event.type == "content_block_delta" and event.delta.type == "input_json_delta":
            tool_use_arguments += event.delta.partial_json
        elif event.type == "content_block_stop" and hasattr(event, 'content_block') and event.content_block.type == "tool_use":
            tool_use_arguments = json.loads(tool_use_arguments)
            yield Message(
                model=model,
                role=role,
                content=[Content(type="tool_use", tool_use=[ToolUse(id=tool_use_id, name=tool_use_name, arguments=tool_use_arguments)], role=role, stop_reason="")]
            )
        elif event.type == "message_stop":
            yield Message(
                model=model,
                role=role,
                content=[Content(type="text", text="", role=role, stop_reason="")],
                usage=Usage(input_tokens=event.message.usage.input_tokens, output_tokens=event.message.usage.output_tokens)
            )


class ClaudeChatModel(LLM):
    def __init__(self, llm_name: str = "claude-3-5-sonnet-20240620", **kwargs) -> None:
        self.llm_name = llm_name
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        self.aclient = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def _format_tools(self, tools: List[BaseModel], tool_choice: str):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        tools, tool_choice = self._check_tool_choice(tools, tool_choice)

        tools_formatted = format_tools(tools, mode=Mode.ANTHROPIC_TOOLS)

        if tool_choice:
            # If the tool_choice is a named tool, then apply correct formatting
            if tool_choice in [tool['title'] for tool in tools]:
                tool_choice = {"type": "tool", "name": tool_choice}
            else: # if it's required or auto, then apply the correct formatting
                tool_choice = (
                    {"type": "any"} if tool_choice == "required" else {"type": tool_choice}
                )  # map "required" to "any"

        return tools_formatted, tool_choice

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
        seed: int = None,
    ):
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
        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        with self.client.messages.stream(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
        ) as stream:

            for event in map_anthropic_stream(stream):
                yield event

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ):
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
        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        with await self.aclient.messages.stream(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
        ) as stream:

            async for event in map_anthropic_stream(stream):
                yield event

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
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
        str
            The generated text.
        """

        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        message = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
        )

        return map_anthropic_message(message)

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
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
        str
            The generated text.
        """
        
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        message = await self.aclient.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
        )

        return map_anthropic_message(message)