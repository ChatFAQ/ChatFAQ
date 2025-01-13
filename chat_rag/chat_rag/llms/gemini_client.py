import os
from typing import Dict, List, Union

from google import genai
from google.genai.types import Part, Content, GenerateContentConfig, Tool, ToolConfig, FunctionCallingConfig
from pydantic import BaseModel

from chat_rag.llms.base_llm import LLM
from chat_rag.llms.format_tools import Mode, format_tools


class GeminiChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "gemini-1.5-flash-002",
        api_key: str = os.getenv("GOOGLE_API_KEY"),
        vertexai: bool = False,
        project: str = None,
        location: str = None,
        **kwargs,
    ):
        """
        Initialize the GeminiChatModel. Only provide the project and location if using VertexAI.
        """
        if vertexai:
            assert project is not None and location is not None, "Project and location must be provided if vertexai is True"
        self.client = genai.Client(api_key=api_key, vertexai=vertexai, project=project, location=location)
        self.llm_name = llm_name

    def _format_tools(self, tools: List[BaseModel], tool_choice: str = None):
        """
        Format the tools from a generic BaseModel to the Gemini format.
        """
        tools, tool_choice = self._check_tool_choice(tools, tool_choice)

        tools_formatted = format_tools(tools, mode=Mode.GEMINI_TOOLS)
        tools_formatted = [Tool(function_declarations=[tool]) for tool in tools_formatted]

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool['title'] for tool in tools]:
            tool_choice = ToolConfig(function_calling_config=FunctionCallingConfig(mode="ANY", allowed_function_names=[tool_choice]))
        elif tool_choice == "required":
            tool_choice = ToolConfig(function_calling_config=FunctionCallingConfig(mode="ANY", allowed_function_names=[tool['title'] for tool in tools]))
        elif tool_choice == "auto":
            tool_choice = ToolConfig(function_calling_config=FunctionCallingConfig(mode="AUTO"))
        return tools_formatted, tool_choice

    def _extract_tool_info(self, message) -> List[Dict]:
        """
        Format the tool information from the gemini response to a standard format.
        """
        tools = []
        if message.parts:
            for part in message.parts:
                if hasattr(part, "function_call"):
                    tools.append(
                        {
                            "id": None,  # Gemini doesn't provide an ID
                            "name": part.function_call.name,
                            "args": part.function_call.args,
                        }
                    )
        return tools

    def _map_role(self, role: str) -> str:
        """Map chat roles to Gemini roles."""
        return "model" if role == "assistant" else role

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
        system_prompt = None
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)["content"]
        contents = [Content(parts=[Part(text=message["content"])], role=self._map_role(message["role"])) for message in messages]

        response = self.client.models.generate_content_stream(
            model=self.llm_name,
            contents=contents,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                seed=seed,
            ),
        )
        for chunk in response:
            if chunk.text is not None:
                yield chunk.text  # return the delta text message

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
        contents = [Content(parts=[Part(text=message["content"])], role=self._map_role(message["role"])) for message in messages]

        response = self.client.aio.models.generate_content_stream(
            model=self.llm_name,
            contents=contents,
            config=GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                seed=seed,
            ),
        )
        async for chunk in response:
            if chunk.text is not None:
                yield chunk.text

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
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
        contents = [Content(parts=[Part(text=message["content"])], role=self._map_role(message["role"])) for message in messages]
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools}
            if tool_choice:
                tool_kwargs["tool_config"] = tool_choice

        response = self.client.models.generate_content(
            model=self.llm_name,
            contents=contents,
            config=GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                seed=seed,
                **tool_kwargs,
            ),
        )

        if response.candidates:
            message = response.candidates[0].content
            if any([hasattr(part, "function_call") for part in message.parts]):
                return self._extract_tool_info(message)
            text = ""
            for part in message.parts:
                text += part.text if part.text else ""
            return text
        return None

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
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
        str | List
            The generated text or a list of tool calls.
        """
        contents = [Content(parts=[Part(text=message["content"])], role=self._map_role(message["role"])) for message in messages]
        tool_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools}
            if tool_choice:
                tool_kwargs["tool_config"] = tool_choice

        response = await self.client.aio.models.generate_content(
            model=self.llm_name,
            contents=contents,
            config=GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                seed=seed,
                **tool_kwargs,
            ),
        )

        if response.candidates:
            message = response.candidates[0].content
            if any([hasattr(part, "function_call") for part in message.parts]):
                return self._extract_tool_info(message)
            text = ""
            for part in message.parts:
                text += part.text if part.text else ""
            return text
        return None