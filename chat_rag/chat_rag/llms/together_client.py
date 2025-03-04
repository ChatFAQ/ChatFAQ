import json
from typing import Callable, Dict, List, Union

from together import AsyncTogether, Together

from chat_rag.llms.base_llm import LLM
from chat_rag.llms.format_tools import Mode, format_tools
from chat_rag.llms.types import Content, Message, ToolUse, Usage


class TogetherChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Default to a Together model
        api_key: str = None,
        **kwargs,
    ):
        self.together_client = Together(api_key=api_key)
        self.async_together_client = AsyncTogether(api_key=api_key)
        self.llm_name = llm_name
        # Call the superclass constructor to set up common attributes

    def _format_tools(
        self, tools: List[Union[Callable, Dict]], tool_choice: str = None
    ):
        """
        Format the tools from a openai dict or a callable function to the OpenAI format, which is the format that Together uses.
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
        Convert standard chat messages to Together's format.
        In Together, not all models like Llama 3.1 support a list of contents as a message so we need to concatenate the texts.
        Also, it seems that you don't add the tool calls to the message, only the tool results. https://docs.together.ai/docs/function-calling
        """

        def format_content(message: Message):
            content = ""
            tool_results = []

            if isinstance(message.content, str):
                content = message.content
            else:
                for msg_content in message.content:
                    if msg_content.type == "text":
                        content += msg_content.text
                    elif msg_content.type == "tool_result":
                        tool_results.append(
                            {
                                "tool_call_id": msg_content.tool_result.id,
                                "role": "tool",
                                "name": msg_content.tool_result.name,
                                "content": msg_content.tool_result.result,
                            }
                        )

            return content, tool_results

        messages_formatted = []
        for message in messages:
            if isinstance(message, Dict):
                message = Message(**message)
            content, tool_results = format_content(message)
            # If there are tool results, then there are only tool results and no content or tool calls for this turn
            if tool_results:
                messages_formatted.extend(tool_results)
            elif content:
                messages_formatted.append(
                    {
                        "role": message.role,
                        "content": content,
                    }
                )
        return messages_formatted

    def _map_together_message(self, message) -> Message:
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

        usage = Usage(
            input_tokens=message.usage.prompt_tokens,
            output_tokens=message.usage.completion_tokens,
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
        **kwargs,
    ):
        """
        Stream the response from the model.
        """
        messages = self._format_messages(messages)

        response = self.together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                return
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    async def astream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        **kwargs,
    ):
        """
        Async stream the response from the model.
        """
        messages = self._format_messages(messages)

        response = await self.async_together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
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
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
    ) -> Message:
        """
        Generate text from a prompt using the model.
        """
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        messages = self._format_messages(messages)

        response = self.together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        return self._map_together_message(response)

    async def agenerate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        **kwargs,
    ) -> Message | List:
        """
        Generate text from a prompt using the model.
        """
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        messages = self._format_messages(messages)

        response = await self.async_together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        return self._map_together_message(response)

    def parse(
        self,
        messages: List[Union[Dict, Message]],
        schema: Dict,
        **kwargs,
    ) -> Message:
        """
        Parse the response using Together's client.
        """
        messages = self._format_messages(messages)

        response = self.together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            response_format={
                "type": "json_object",
                "schema": schema,
            },
        )
        return json.loads(response.choices[0].message.content)

    async def aparse(
        self,
        messages: List[Union[Dict, Message]],
        schema: Dict,
        **kwargs,
    ) -> Message:
        """
        Async parse the response using Together's client.
        """
        messages = self._format_messages(messages)
        response = await self.async_together_client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            response_format={
                "type": "json_object",
                "schema": schema,
            },
        )
        return json.loads(response.choices[0].message.content)
