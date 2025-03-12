import json
from typing import Callable, Dict, List, Union

from openai import AsyncOpenAI, OpenAI, NOT_GIVEN
from openai.lib._pydantic import _ensure_strict_json_schema

from chat_rag.llms.types import Content, Message, ToolUse, Usage

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
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.llm_name = llm_name

    def _format_tools(
        self, tools: List[Union[Callable, Dict]], tool_choice: str = None
    ):
        """
        Format the tools from a openai dict or a callable function to the OpenAI format.
        """
        tools_formatted, tool_choice = format_tools(
            tools, tool_choice, mode=Mode.OPENAI_TOOLS
        )

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool["function"]["name"] for tool in tools_formatted]:
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
                # Send it as a string to maintain compatibility with the old format that some companies use for their openai api
                return message.content, [], [] 
            else:
                for content in message.content:
                    if content.type == "text":
                        content_list.append(
                            {"type": content.type, "text": content.text}
                        )
                    elif content.type == "tool_use":
                        part = {
                            "type": "function",
                            "id": content.tool_use.id,
                            "function": {
                                "name": content.tool_use.name,
                                "arguments": str(content.tool_use.args),
                            },
                        }
                        tool_calls.append(part)
                    elif content.type == "tool_result":
                        tool_results.append(
                            {
                                "tool_call_id": content.tool_result.id,
                                "role": "tool",
                                "content": content.tool_result.result,
                            }
                        )

            return content_list, tool_calls, tool_results

        messages_formatted = []
        for message in messages:
            if isinstance(message, Dict):
                message = Message(**message)
            content, tool_calls, tool_results = format_content(message)
            # If there are tool results, then there are only tool results and no content or tool calls for this turn
            if tool_results:
                messages_formatted.extend(tool_results)
            else:
                messages_formatted.append(
                    {
                        "role": message.role,
                        "content": content if content else None,
                        "tool_calls": tool_calls if tool_calls else None,
                    }
                )
        return messages_formatted

    def _map_openai_message(self, message) -> Message:
        """
        Map the OpenAI message to the standard message format.
        """
        content_list = []
        content = message.choices[0].message
        if content.content:
            content_list = [Content(type="text", text=content.content)]
        if content.tool_calls:
            content_list = [
                Content(
                    type="tool_use",
                    tool_use=ToolUse(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        args=json.loads(tool_call.function.arguments),
                    ),
                )
                for tool_call in content.tool_calls
            ]
        
        usage = None
        if message.usage:
            usage = Usage(
                input_tokens=message.usage.prompt_tokens,
                output_tokens=message.usage.completion_tokens,
                cache_creation_read_tokens=message.usage.prompt_tokens_details.cached_tokens,
            )
        return Message(
            role=content.role,
            content=content_list,
            tool_calls=content.tool_calls,
            usage=usage,
        )

    def stream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        thinking: str = NOT_GIVEN,
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
            max_completion_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
            reasoning_effort=thinking,
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
        thinking: str = NOT_GIVEN,
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
            max_completion_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=True,
            reasoning_effort=thinking,
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
        thinking: str = NOT_GIVEN,
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
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        messages = self._format_messages(messages)

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            seed=seed,
            reasoning_effort=thinking,
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
        thinking: str = NOT_GIVEN,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
    ) -> Message | List:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        Message | List
            The generated message.
        """
        messages = self._format_messages(messages)

        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            seed=seed,
            reasoning_effort=thinking,
            n=1,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        return self._map_openai_message(response)

    def parse(
        self,
        messages: List[Union[Dict, Message]],
        schema: Dict,
        **kwargs,
    ) -> Dict:
        """
        Parse the response from the model into a structured format.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        schema : Dict
            The schema to use for the response. It must be a pydantic model json schema, it can be generated using the `model_json_schema` method of the pydantic model.
        Returns
        -------
        Dict
            The parsed message.
        """
        messages = self._format_messages(messages)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "schema": _ensure_strict_json_schema(schema, path=(), root=schema),
                "name": schema["title"],
                "strict": True,
            },
        }

        response = self.client.beta.chat.completions.parse(
            model=self.llm_name,
            messages=messages,
            response_format=response_format,
        )

        return json.loads(response.choices[0].message.content)
    
    async def aparse(
        self,
        messages: List[Union[Dict, Message]],
        schema: Dict,
        **kwargs,
    ) -> Dict:
        """
        Parse the response from the model into a structured format.
        """
        messages = self._format_messages(messages)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "schema": _ensure_strict_json_schema(schema, path=(), root=schema),
                "name": schema["title"],
                "strict": True,
            },
        }

        response = await self.aclient.beta.chat.completions.parse(
            model=self.llm_name,
            messages=messages,
            response_format=response_format,
        )

        return json.loads(response.choices[0].message.content)
