import os
from typing import Callable, Dict, List, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic._types import NOT_GIVEN

from chat_rag.llms.types import Content, Message, ToolUse, Usage

from .base_llm import LLM
from .format_tools import Mode, format_tools


class ClaudeChatModel(LLM):
    def __init__(self, llm_name: str = "claude-3-7-sonnet-latest", **kwargs) -> None:
        self.llm_name = llm_name
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        self.aclient = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def _format_tools(
        self, tools: List[Union[Callable, Dict]], tool_choice: str, messages: List[Dict[str, str]]
    ):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        tools_formatted, tool_choice = format_tools(tools, tool_choice, mode=Mode.ANTHROPIC_TOOLS)

        # If any messages have cache_control, add cache_control to the last tool so they are cached also
        if any(message.get("cache_control") for message in messages):
            if tools_formatted:
                tools_formatted[-1]["cache_control"] = {"type": "ephemeral"}

        if tool_choice:
            # If the tool_choice is a named tool, then apply correct formatting
            if tool_choice in [tool["name"] for tool in tools_formatted]:
                tool_choice = {"type": "tool", "name": tool_choice}
            else:  # if it's required or auto, then apply the correct formatting
                tool_choice = (
                    {"type": "any"}
                    if tool_choice == "required"
                    else {"type": tool_choice}
                )  # map "required" to "any"

        return tools_formatted, tool_choice

    def _format_messages(self, messages: List[Union[Dict, Message]]) -> List[Dict]:
        """
        Convert standard chat messages to Anthropic's format.
        """

        def format_content(message: Union[Dict, Message]):

            if isinstance(message, Dict):
                message = Message(**message)

            if isinstance(message.content, str):
                content_list = [{"type": "text", "text": message.content}]
            else:
                content_list = []
                for content in message.content:
                    if content.type == "text":
                        part = {"type": content.type, "text": content.text}
                    elif content.type == "tool_use":
                        part = {
                            "type": content.type,
                            "id": content.tool_use.id,
                            "name": content.tool_use.name,
                            "input": content.tool_use.args,
                        }
                    elif content.type == "tool_result":
                        part = {
                            "type": content.type,
                            "tool_use_id": content.tool_result.id,
                            "content": content.tool_result.result,
                        }
                    content_list.append(part)

            # Add cache_control if present in original message
            if message.cache_control:
                content_list[-1]["cache_control"] = {"type": "ephemeral"}

            return content_list

        messages_formatted = [
            {"role": message["role"] if isinstance(message, Dict) else message.role, "content": format_content(message)}
            for message in messages
        ]

        system_prompt = NOT_GIVEN
        # Add system message if present
        if messages_formatted[0]["role"] == "system":
            system_prompt = messages_formatted.pop(0)["content"][0]["text"]

        return messages_formatted, system_prompt

    def _map_anthropic_message(self, message) -> Message:
        """
        Convert Anthropic's message format to our Message format.
        """
        content_list = []
        for part in message.content:
            # TODO: Handle thinking output block types
            if part.type == "text":
                content_list.append(
                    Content(
                        type="text",
                        text=part.text,
                    )
                )
            elif part.type == "tool_use":
                content_list.append(
                    Content(
                        type="tool_use",
                        tool_use=ToolUse(id=part.id, name=part.name, args=part.input),
                    )
                )

        return Message(
            role="assistant",
            content=content_list,
            stop_reason=message.stop_reason,
            usage=Usage(
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                cache_creation_input_tokens=message.usage.cache_creation_input_tokens,
                cache_creation_read_tokens=message.usage.cache_read_input_tokens,
            ),
        )

    def stream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        thinking: dict = None,
        **kwargs,
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
        messages, system_prompt = self._format_messages(messages)

        stream = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            thinking=thinking if thinking else NOT_GIVEN,
        )

        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    pass # Pass for now until I figure out a common interface for thinking
                    # yield event.delta.thinking
                elif event.delta.type == "text_delta":
                    yield event.delta.text

    async def astream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        thinking: dict = None,
        **kwargs,
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
        messages, system_prompt = self._format_messages(messages)

        stream = await self.aclient.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            thinking=thinking if thinking else NOT_GIVEN,
        )

        async for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    pass # Pass for now until I figure out a common interface for thinking
                    # yield event.delta.thinking
                elif event.delta.type == "text_delta":
                    yield event.delta.text

    def generate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        thinking: dict = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
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
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice, messages)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        messages, system_prompt = self._format_messages(messages)

        message = self.client.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
            thinking=thinking if thinking else NOT_GIVEN,
        )

        return self._map_anthropic_message(message)

    async def agenerate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        thinking: dict = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
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
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice, messages)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

        messages, system_prompt = self._format_messages(messages)

        message = await self.aclient.messages.create(
            model=self.llm_name,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **tool_kwargs,
            thinking=thinking if thinking else NOT_GIVEN,
        )

        return self._map_anthropic_message(message)
