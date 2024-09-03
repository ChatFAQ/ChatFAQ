import json
import os
from typing import Dict, List, Union, Iterator

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


def map_openai_stream(stream: Iterator) -> Iterator[Message]:
    """
    Process an OpenAI stream and return a stream of messages. 
    Text is streamed as text_delta.
    The tool use is not streamed, it is accumulated and returned as a single tool use.
    In the last message, the usage is returned.
    """
    tool_use_name = None
    tool_use_id = None
    tool_use_arguments = None
    model = None
    created = None
    role = None

    def send_tool_message():
        nonlocal tool_use_name, tool_use_id, tool_use_arguments
        if tool_use_name and tool_use_id and tool_use_arguments:
            message = Message(
                model=model,
                role=role,
                content=[Content(type="tool_use", tool_use=[ToolUse(id=tool_use_id, name=tool_use_name, arguments=json.loads(tool_use_arguments))], role=role, stop_reason="")],
                )
            # reset tool use variables
            tool_use_name = None
            tool_use_id = None
            tool_use_arguments = None
            return message
        else:
            return None

    for event in stream:
        if model is None: # first empty message
           model = event.model
           role = event.choices[0].delta.role
           created = event.created
        
        if not event.choices and event.usage: # last message and it's empty
           message = send_tool_message() # send the last tool message
           if message:
              yield message
           yield Message(model=model, created=created, content=[Content(type="text_delta", text="", role=role, stop_reason="")], usage=Usage(input_tokens=event.usage.prompt_tokens, output_tokens=event.usage.completion_tokens))
        elif event.choices[0].delta.tool_calls and event.choices[0].delta.tool_calls[0].id: # first message of a tool use
           message = send_tool_message()
           if message:
              yield message
           tool_use_name = event.choices[0].delta.tool_calls[0].function.name
           tool_use_id = event.choices[0].delta.tool_calls[0].id
           tool_use_arguments = "" # start accumulating arguments
        elif event.choices[0].delta.tool_calls and tool_use_name: # accumulating arguments for a tool use
            tool_use_arguments += event.choices[0].delta.tool_calls[0].function.arguments
        else: # normal text message
           message = send_tool_message()
           if message:
              yield message
           content_blocks = []
           for choice in event.choices:
              if choice.finish_reason == "stop" or choice.finish_reason == "content_filter" or choice.finish_reason == "tool_calls":
                  content_blocks.append(Content(stop_reason=choice.finish_reason, role=role, type="text_delta"))
                  yield Message(model=model, created=created, content=content_blocks)     
              elif choice.delta.content:
                  content_blocks.append(Content(text=choice.delta.content, stop_reason="", role=role, type="text_delta"))
                  yield Message(model=model, created=created, content=content_blocks)  


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

        tools_formatted = format_tools(tools, mode=Mode.TOOLS)

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool['function']['name'] for tool in tools_formatted]:
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
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
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
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
            stream_options={"include_usage": True},
            tools=tools,
            tool_choice=tool_choice,
        )
        for event in map_openai_stream(response):
            yield event

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
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
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
            stream_options={"include_usage": True},
            tools=tools,
            tool_choice=tool_choice,
        )
        for event in map_openai_stream(response):
            yield event

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