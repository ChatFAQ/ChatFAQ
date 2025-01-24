import os
from typing import Dict, List, Union

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from chat_rag.llms import Content, Message, ToolUse, Usage

from .base_llm import LLM
from .format_tools import Mode, format_tools

class OpenAIChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "gpt-4o",
        base_url: str = None,
        api_key: str = None,
        **kwargs,
    ):

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
    
    def _format_messages(self, messages: List[Union[Dict, Message]]) -> List[Dict]:
        """
        Convert standard chat messages to OpenAI's format.
        """
        def format_content(message: Message):
            content_list = []
            tool_calls = []
            tool_results = []
            if isinstance(message.content, str):
                content_list = [{"type": "text", "text": message.content}]
            else:
                for content in message.content:
                    if content.type == "text":
                        content_list.append({"type": content.type, "text": content.text})
                    elif content.type == "tool_use":
                        part = {
                            "type": "function",
                            "id": content.tool_use.id,
                            "function": {
                                "name": content.tool_use.name,
                                "arguments": content.tool_use.args,
                            },
                        }
                        tool_calls.append(part)
                    elif content.type == "tool_result":
                        tool_results.append(
                            {
                                "id": content.tool_result.id,
                                "output": content.tool_result.result,
                            }
                        )

            return content_list, tool_calls, tool_results

        messages = []
        for message in messages:
            content, tool_calls, tool_results = format_content(message)
            role = message.role if not tool_results else "tool"
            messages.append(
                {
                    "role": role,
                    "content": content if content else None,
                    "tool_calls": tool_calls if tool_calls else None,
                }
            )
        return messages
    
    def _map_openai_message(self, message) -> Message:
        """
        Map the OpenAI message to the standard message format.
        """
        content_list = []
        content = message.choices[0].message
        if content.content:
            content_list = [Content(type="text", text=content.content)]
        if content.tool_calls:
            content_list = [Content(type="tool_use", tool_use=ToolUse(id=tool_call.id, name=tool_call.function.name, args=tool_call.function.arguments)) for tool_call in content.tool_calls]

        usage = Usage(input_tokens=message.usage.prompt_tokens, output_tokens=content.usage.completion_tokens, cache_creation_read_tokens=message.usage.prompt_tokens_details.cached_tokens)
        return Message(role=content.role, content=content_list, tool_calls=content.tool_calls, usage=usage)

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        **kwargs,
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
        messages = self._format_messages(messages)

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
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        **kwargs,
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
        messages = self._format_messages(messages)
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
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
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

        messages = self._format_messages(messages)

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

        return self._map_openai_message(response)

    async def agenerate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
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
        messages = self._format_messages(messages)

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

        return self._map_openai_message(response)
