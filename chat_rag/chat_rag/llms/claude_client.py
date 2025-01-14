import os
from typing import Dict, List, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic._types import NOT_GIVEN
from pydantic import BaseModel

from .base_llm import LLM
from .format_tools import Mode, format_tools


class ClaudeChatModel(LLM):
    def __init__(self, llm_name: str = "claude-3-opus-20240229", **kwargs) -> None:
        self.llm_name = llm_name
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        self.aclient = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def _format_tools(self, tools: List[BaseModel], tool_choice: str, messages: List[Dict[str, str]]):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        tools, tool_choice = self._check_tool_choice(tools, tool_choice)

        tools_formatted = format_tools(tools, mode=Mode.ANTHROPIC_TOOLS)

        # If any messages have cache_control, add cache_control to the last tool so they are cached also
        if any(message.get("cache_control") for message in messages):
            if tools_formatted:
                tools_formatted[-1]["cache_control"] = {"type": "ephemeral"}

        if tool_choice:
            # If the tool_choice is a named tool, then apply correct formatting
            if tool_choice in [tool['title'] for tool in tools]:
                tool_choice = {"type": "tool", "name": tool_choice}
            else: # if it's required or auto, then apply the correct formatting
                tool_choice = (
                    {"type": "any"} if tool_choice == "required" else {"type": tool_choice}
                )  # map "required" to "any"

        return tools_formatted, tool_choice

    def _extract_tool_info(self, content: List) -> List[Dict]:
        """
        Format the tool information from the anthropic response to a standard format.
        Claude only calls one tool at a time but we return a list for consistency.
        """
        tool = {}
        for block in content:
            if block.type == "tool_use":
                tool["id"] = block.id
                tool["name"] = block.name
                tool["args"] = block.input
            elif block.type == "text":
                tool["text"] = block.text
        return [tool]

    def _format_messages(messages: List[Dict[str, str]]) -> List[Dict]:
        """
        Convert standard chat messages to Anthropic's format.
        
        Input format:
        {"role": "user", "content": "hello", "cache_control": {"type": "ephemeral"}}
        
        Output format:
        {"role": "user", "content": [{"type": "text", "text": "hello", "cache_control": {"type": "ephemeral"}}]}
        """
        def format_content(message):
            content = message["content"]
            part = {"type": "text", "text": content}
            
            # Add cache_control if present in original message
            if "cache_control" in message:
                part["cache_control"] = message["cache_control"]
                
            return [part]

        return [
            {
                "role": message["role"],
                "content": format_content(message)
            }
            for message in messages
        ]

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
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
        messages = self._format_messages(messages)
        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        stream = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
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
        messages = self._format_messages(messages)
        system_prompt = NOT_GIVEN
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]

        stream = await self.aclient.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
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
        str
            The generated text.
        """
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice, messages)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        messages = self._format_messages(messages)
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

        content = message.content
        if any([x.type == "tool_use" for x in content]):
            return self._extract_tool_info(content)

        return content[0].text

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
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
        str
            The generated text.
        """
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice, messages)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        messages = self._format_messages(messages)
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

        content = message.content
        if any([x.type == "tool_use" for x in content]):
            return self._extract_tool_info(content)
        return message.content[0].text