import os
from typing import Callable, Dict, List, Tuple, Union

from google import genai
from google.genai.types import (
    Content as GeminiContent,
    CreateCachedContentConfig,
    FunctionCallingConfig,
    GenerateContentConfig,
    Part,
    Tool,
    ToolConfig,
    GenerateContentResponse,
    FunctionCall,
    FunctionResponse,
)

from chat_rag.llms import Message, Usage, Content, ToolUse, ToolResult
from chat_rag.llms.base_llm import LLM
from chat_rag.llms.format_tools import Mode, format_tools


class GeminiChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "gemini-1.5-flash-002",
        vertexai: bool = False,
        project: str = None,
        location: str = None,
        **kwargs,
    ):
        """
        Initialize the GeminiChatModel. Only provide the project and location if using VertexAI.
        """
        if vertexai:
            assert project is not None and location is not None, (
                "Project and location must be provided if vertexai is True"
            )

        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY", None), 
            vertexai=vertexai, 
            project=project, 
            location=location
        )
        self.llm_name = llm_name

    def _format_tools(self, tools: List[Union[Callable, Dict]], tool_choice: str = None):
        """
        Format the tools from a generic BaseModel to the Gemini format.
        """
        tools_formatted = format_tools(tools, mode=Mode.GEMINI_TOOLS)
        tool_choice = self._check_tool_choice(tools_formatted, tool_choice)

        tools_formatted = [
            Tool(function_declarations=[tool]) for tool in tools_formatted
        ]

        # If the tool_choice is a named tool, then apply correct formatting
        if tool_choice in [tool["title"] for tool in tools]:
            tool_choice = ToolConfig(
                function_calling_config=FunctionCallingConfig(
                    mode="ANY", allowed_function_names=[tool_choice]
                )
            )
        elif tool_choice == "required":
            tool_choice = ToolConfig(
                function_calling_config=FunctionCallingConfig(
                    mode="ANY", allowed_function_names=[tool["title"] for tool in tools]
                )
            )
        elif tool_choice == "auto":
            tool_choice = ToolConfig(
                function_calling_config=FunctionCallingConfig(mode="AUTO")
            )
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
    
    def _map_gemini_message(self, response: GenerateContentResponse) -> Message:
        """
        Maps a Gemini Content object to a chat_rag Message object.
        """
        contents: List[Content] = []
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    contents.append(Content(type="text", text=part.text))
                elif part.function_call:
                    contents.append(
                        Content(
                            type="tool_use",
                            tool_use=ToolUse(
                                name=part.function_call.name,
                                args=part.function_call.args,
                            ),
                        )
                    )

        usage = response.usage_metadata
        return Message(
            role="assistant",
            content=contents if contents else "", # if no parts, set content to empty string
            usage=Usage(
                input_tokens=usage.prompt_token_count if usage else 0,
                output_tokens=usage.candidates_token_count if usage else 0,
                cache_creation_input_tokens=usage.total_token_count if usage else 0,
                cache_creation_read_tokens=0
            ),
            stop_reason=response.candidates[0].finish_reason,
        )
    
    def _create_cache(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        cache_config: Dict = None,
    ) -> str:
        """
        Create a cache for the given messages.
        
        Parameters
        ----------
        messages : List[Dict[str, str]]
            The messages to cache
        system_prompt : str, optional
            The system prompt
        cache_config : Dict
            Configuration containing cache name and ttl
        
        Returns
        -------
        str
            The cache name
        """
        contents = [
            GeminiContent(
                parts=[Part(text=message["content"])],
                role=self._map_role(message["role"]),
            )
            for message in messages
        ] if messages else None
        
        cached_content = self.client.caches.create(
            model=self.llm_name,
            config=CreateCachedContentConfig(
                contents=contents,
                system_instruction=system_prompt,
                display_name=cache_config.get("name", "default_cache"),
                ttl=f"{cache_config.get('ttl', 3600)}s",
            ),
        )
        return cached_content.name

    async def _acreate_cache(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        cache_config: Dict = None,
    ) -> str:
        """
        Create a cache for the given messages.
        
        Parameters
        ----------
        messages : List[Dict[str, str]]
            The messages to cache
        system_prompt : str, optional
            The system prompt
        cache_config : Dict
            Configuration containing cache name and ttl
        
        Returns
        -------
        str
            The cache name
        """
        contents = [
            GeminiContent(
                parts=[Part(text=message["content"])],
                role=self._map_role(message["role"]),
            )
            for message in messages
        ] if messages else None
        
        cached_content = await self.client.aio.caches.create(
            model=self.llm_name,
            config=CreateCachedContentConfig(
                contents=contents,
                system_instruction=system_prompt,
                display_name=cache_config.get("name", "default_cache"),
                ttl=f"{cache_config.get('ttl', 3600)}s",
            ),
        )
        return cached_content.name

    def _prepare_messages(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float,
        max_tokens: int,
        seed: int,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
    ) -> Tuple[str, List[Dict], List[Content], Dict]:
        """
        It prepares the messages for the Gemini client. In case there is caching, it splits the messages into messages to be cached and new messages to be sent to the model.
        
        Returns
        -------
        Tuple[str, List[Dict], List[Content], Dict]
            system_prompt, cached_messages, content_messages, config_kwargs
        """
        def format_content(message: Message):
            parts = []
            tool_calls = []
            tool_results = []
            if isinstance(message.content, str):
                parts = [Part(text=message.content)]
            else:
                for content in message.content:
                    if content.type == "text":
                        parts.append(Part(text=content.text))
                    elif content.type == "tool_use":
                        tool_calls.append(Part(function_call=FunctionCall(id=content.tool_use.id, name=content.tool_use.name, args=content.tool_use.args)))
                    elif content.type == "tool_result":
                        tool_results.append(Part(function_response=FunctionResponse(id=content.tool_result.id, name=content.tool_result.name, response=content.tool_result.result)))
            return parts

        # Extract system prompt if present
        system_prompt = None
        if messages[0].role == "system":
            system_prompt = messages.pop(0).content

        # Find the last message with cache_control
        cache_split_idx = 0
        for idx, msg in enumerate(messages):
            if msg.cache_control:
                cache_split_idx = idx + 1

        # Split messages into cached and new
        cached_messages = messages[:cache_split_idx] # These will be cached
        new_messages = messages[cache_split_idx:] # These will be sent to the model

        # Prepare contents for new messages
        contents = [
            GeminiContent(
                parts=format_content(message),
                role=self._map_role(message.role),
            )
            for message in new_messages
        ]

        cached_contents = [
            GeminiContent(
                parts=format_content(message),
                role=self._map_role(message.role),
            )
            for message in cached_messages
        ]

        # Prepare tool configuration
        tool_kwargs = {}
        if tools:
            tools_formatted, tool_choice = self._format_tools(tools, tool_choice)
            tool_kwargs = {"tools": tools_formatted}
            if tool_choice:
                tool_kwargs["tool_config"] = tool_choice

        config_kwargs = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "seed": seed,
            "automatic_function_calling": {"disable": True},
            **tool_kwargs,
        }

        return system_prompt, cached_contents, contents, config_kwargs

    def stream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 4096,
        seed: int = None,
        cache_config: Dict = None,
    ):
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        cache_config: Dict
            The cache configuration. This contains the cache name and ttl. 
        Returns
        -------
        str
            The generated text.
        """
        system_prompt, cached_messages, contents, config_kwargs = self._prepare_messages(
            messages, temperature, max_tokens, seed
        )

        # If we have messages to cache and cache_config
        if (cached_messages and cache_config) or (system_prompt and cache_config):
            # List through all caches to find the real cache name
            caches = self.client.caches.list()
            name = None
            for cache in caches:
                if cache.display_name == cache_config["name"]:
                    name = cache.name
                    break
                    
            if name:  # If the cache exists, use it
                config_kwargs["cached_content"] = name
                response = self.client.models.generate_content_stream(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
            else:
                # Create cache and retry
                cache_name = self._create_cache(
                    cached_messages, system_prompt, cache_config
                )
                config_kwargs["cached_content"] = cache_name
                response = self.client.models.generate_content_stream(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
        else:
            # Add system prompt to the config
            config_kwargs["system_instruction"] = system_prompt
            # No caching needed
            response = self.client.models.generate_content_stream(
                model=self.llm_name,
                contents=contents,
                config=GenerateContentConfig(**config_kwargs),
            )

        for chunk in response:
            if chunk.text is not None:
                yield chunk.text

    async def astream(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 4096,
        seed: int = None,
        cache_config: Dict = None,
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
        system_prompt, cached_messages, contents, config_kwargs = self._prepare_messages(
            messages, temperature, max_tokens, seed
        )

        # If we have messages to cache and cache_config
        if (cached_messages and cache_config) or (system_prompt and cache_config):
            # List through all caches to find the real cache name
            caches = self.client.caches.list()
            name = None
            for cache in caches:
                if cache.display_name == cache_config["name"]:
                    name = cache.name
                    break

            if name:  # If the cache exists, use it
                config_kwargs["cached_content"] = name
                response = self.client.aio.models.generate_content_stream(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
            else:
                # Create cache and retry
                cache_name = self._create_cache(
                    cached_messages, system_prompt, cache_config
                )
                config_kwargs["cached_content"] = cache_name
                response = self.client.aio.models.generate_content_stream(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
        else:
            # Add system prompt to the config
            config_kwargs["system_instruction"] = system_prompt
            # No caching needed
            response = self.client.aio.models.generate_content_stream(
                model=self.llm_name,
                contents=contents,
                config=GenerateContentConfig(**config_kwargs),
            )

        async for chunk in response:
            if chunk.text is not None:
                yield chunk.text

    def generate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 4096,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        cache_config: Dict = None,
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
        system_prompt, cached_messages, contents, config_kwargs = self._prepare_messages(
            messages, temperature, max_tokens, seed, tools, tool_choice
        )

        # If we have messages to cache and cache_config
        if (cached_messages and cache_config) or (system_prompt and cache_config):
            # List through all caches is not optimal, it adds almost a second to the response time but it's the only way to get the real cache name for now
            caches = self.client.caches.list() 
            name = None
            for cache in caches:
                if cache.display_name == cache_config["name"]:
                    name = cache.name
                    break
            if name: # If the cache exists, use it
                config_kwargs["cached_content"] = name
                response = self.client.models.generate_content(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
            else:
                # Create cache and retry
                cache_name = self._create_cache(
                    cached_messages, system_prompt, cache_config
                )
                config_kwargs["cached_content"] = cache_name
                response = self.client.models.generate_content(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
        else:
            # Add system prompt to the config
            config_kwargs["system_instruction"] = system_prompt
            # No caching needed
            response = self.client.models.generate_content(
                model=self.llm_name,
                contents=contents,
                config=GenerateContentConfig(**config_kwargs),
            )
        return self._map_gemini_message(response)

    async def agenerate(
        self,
        messages: List[Union[Dict, Message]],
        temperature: float = 1.0,
        max_tokens: int = 4096,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
        cache_config: Dict = None,
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
        system_prompt, cached_messages, contents, config_kwargs = self._prepare_messages(
            messages, temperature, max_tokens, seed, tools, tool_choice
        )

        # If we have messages to cache and cache_config
        if (cached_messages and cache_config) or (system_prompt and cache_config):
            # List through all caches is not optimal but it's the only way to get the real cache name for now
            caches = await self.client.aio.caches.list() 
            name = None
            for cache in caches:
                if cache.display_name == cache_config["name"]:
                    name = cache.name
                    break
            if name: # If the cache exists, use it
                config_kwargs["cached_content"] = name
                response = await self.client.aio.models.generate_content(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
            else:
                # Create cache and retry
                cache_name = await self._acreate_cache(
                    cached_messages, system_prompt, cache_config
                )
                config_kwargs["cached_content"] = cache_name
                response = await self.client.aio.models.generate_content(
                    model=self.llm_name,
                    contents=contents,
                    config=GenerateContentConfig(**config_kwargs),
                )
        else:
            # Add system prompt to the config
            config_kwargs["system_instruction"] = system_prompt
            # No caching needed
            response = await self.client.aio.models.generate_content(
                model=self.llm_name,
                contents=contents,
                config=GenerateContentConfig(**config_kwargs),
            )
        return self._map_gemini_message(response)