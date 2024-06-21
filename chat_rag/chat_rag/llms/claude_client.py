import os
from typing import Dict, List

from anthropic import Anthropic, AsyncAnthropic
from instructor import Mode, handle_response_model
from pydantic import BaseModel

from chat_rag.llms import LLM


class ClaudeChatModel(LLM):
    def __init__(self, llm_name: str = "claude-3-opus-20240229", **kwargs) -> None:
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
        self._check_tool_choice(tools, tool_choice)

        tools_formatted = []
        for tool in tools:
            _, tool_formatted = handle_response_model(
                tool, mode=Mode.ANTHROPIC_TOOLS, messages=[]
            )
            tools_formatted.append(tool_formatted["tools"][0])

        if tool_choice:
            # If the tool_choice is a named tool, then apply correct formatting
            if tool_choice in [tool.model_json_schema()['title'] for tool in tools]:
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
        tools: List[BaseModel] = None,
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
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

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
        tools: List[BaseModel] = None,
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
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools, "tool_choice": tool_choice}

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
