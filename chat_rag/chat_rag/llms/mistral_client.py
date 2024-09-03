import json
import os
from typing import Dict, List, Union, Iterator

from mistralai import Mistral
from pydantic import BaseModel

from .base_llm import LLM
from .format_tools import Mode, format_tools
from .message import Content, Message, ToolUse, Usage


def map_mistral_message(mistral_message):
    usage = Usage(
        input_tokens=mistral_message.usage.prompt_tokens,
        output_tokens=mistral_message.usage.completion_tokens
    )
    content_blocks = []
    for choice in mistral_message.choices:
        if choice.message.tool_calls:
            tool_uses = [ToolUse(id=tool_call.id, name=tool_call.function.name, arguments=json.loads(tool_call.function.arguments)) for tool_call in choice.message.tool_calls]
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


def map_mistral_stream(stream: Iterator) -> Iterator[Message]:
    """
    Process a Mistral stream and return a stream of messages. 
    Text is streamed as text_delta.
    The tool use is not streamed, it is accumulated and returned as a single tool use.
    In the last message, the usage is returned.
    """
    model = None
    created = None
    role = None
    for event in stream:
        event = event.data
        if model is None: # first empty message
           model = event.model
           role = event.choices[0].delta.role
           created = event.created

        if event.choices[0].delta.tool_calls:
            tool_uses = [ToolUse(id=tool_call.id, name=tool_call.function.name, arguments=json.loads(tool_call.function.arguments)) for tool_call in event.choices[0].delta.tool_calls]
            yield Message(model=model, created=created, content=[Content(type="tool_use", tool_use=tool_uses, role=role, stop_reason="")])        
        else: # normal text message
           content_blocks = []
           for choice in event.choices:
              if choice.finish_reason == "stop" or choice.finish_reason == "content_filter" or choice.finish_reason == "tool_calls":
                  content_blocks.append(Content(stop_reason=choice.finish_reason, role=role, type="text_delta"))
                  yield Message(model=model, created=created, content=content_blocks)     
              elif choice.delta.content:
                  content_blocks.append(Content(text=choice.delta.content, stop_reason="", role=role, type="text_delta"))
                  yield Message(model=model, created=created, content=content_blocks)

        if event.choices[0].finish_reason and event.usage: # last message and it's empty
           yield Message(model=model, created=created, content=[Content(type="text_delta", text="", role=role, stop_reason="")], usage=Usage(input_tokens=event.usage.prompt_tokens, output_tokens=event.usage.completion_tokens))   


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

        stream = self.client.chat.stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        for chunk in map_mistral_stream(stream):
            yield chunk
            

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

        stream = self.client.chat.stream_async(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        for chunk in map_mistral_stream(stream):
            yield chunk
            

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