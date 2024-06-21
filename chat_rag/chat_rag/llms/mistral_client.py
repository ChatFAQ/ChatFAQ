import os
from typing import Dict, List

from instructor import Mode, handle_response_model
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from pydantic import BaseModel

from chat_rag.llms import LLM


class MistralChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "mistral-large-latest",
        **kwargs,
    ):
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.aclient = MistralAsyncClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
    ) -> List[ChatMessage]:
        """
        Formats the prompt to be used by the model into the correct Mistral format.
        """
        final_messages = [
            ChatMessage(role=message["role"], content=message["content"])
            for message in messages
        ]

        return final_messages

    def _format_tools(self, tools: List[BaseModel], tool_choice: str = None):
        """
        Format the tools from a generic BaseModel to the OpenAI format.
        """
        self._check_tool_choice(tools, tool_choice)

        tools_formatted = []
        for tool in tools:
            _, tool_formatted = handle_response_model(tool, mode=Mode.MISTRAL_TOOLS)
            tools_formatted.append(tool_formatted["tools"][0])

        if tool_choice:
            if tool_choice not in ["required", "auto"]:
                raise ValueError(
                    "Named tool choice is not supported for Mistral, only 'required' or 'auto' is supported."
                )

            tool_choice = (
                "any" if tool_choice == "required" else tool_choice
            )  # map "required" to "any"

        return tools_formatted, tool_choice

    def _extract_tool_info(self, message) -> List[Dict]:
        """
        Format the tool information from the anthropic response to a standard format.
        """
        tools = []
        for tool in message.tool_calls:
            tools.append(
                {
                    "id": tool.id,
                    "name": tool.function.name,
                    "args": tool.function.arguments,
                }
            )

        return tools

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

        messages = self.format_prompt(
            messages=messages,
        )

        for chunk in self.client.chat_stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

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

        messages = self.format_prompt(
            messages=messages,
        )

        async for chunk in self.aclient.chat_stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

        return

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Dict] = None,
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

        messages = self.format_prompt(
            messages=messages,
        )

        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        chat_response = self.client.chat(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        message = chat_response.choices[0].message
        if chat_response.choices[0].finish_reason == "tool_calls":
            return self._extract_tool_info(message)

        return message.content

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Dict] = None,
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

        messages = self.format_prompt(
            messages=messages,
        )
        
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)

        chat_response = await self.aclient.chat(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
            tools=tools,
            tool_choice=tool_choice,
        )

        message = chat_response.choices[0].message
        if chat_response.choices[0].finish_reason == "tool_calls":
            return self._extract_tool_info(message)

        return message.content
