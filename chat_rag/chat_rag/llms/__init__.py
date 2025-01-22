import os
import time
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from chat_rag.llms.base_llm import LLM
from chat_rag.llms.claude_client import ClaudeChatModel
from chat_rag.llms.format_tools import Mode, format_tools
from chat_rag.llms.gemini_client import GeminiChatModel
from chat_rag.llms.mistral_client import MistralChatModel
from chat_rag.llms.openai_client import OpenAIChatModel
from chat_rag.llms.vllm_client import VLLMModel

__all__ = [
    "LLM",
    "OpenAIChatModel",
    "VLLMModel",
    "ClaudeChatModel",
    "MistralChatModel",
    "GGMLModel",
    "HFModel",
    "format_tools",
]


LLM_CLASSES = {
    "claude": ClaudeChatModel,
    "mistral": MistralChatModel,
    "openai": OpenAIChatModel,
    "vllm": VLLMModel,
    "together": OpenAIChatModel,
    "gemini": GeminiChatModel,
}


def load_llm(
    llm_type: str, llm_name: str, base_url: str = None, model_max_length: int = None
) -> LLM:
    # For Together model, set the fixed TOGETHER url
    api_key = None
    if llm_type == "together":
        base_url = "https://api.together.xyz/v1"
        api_key = os.environ.get("TOGETHER_API_KEY")

    llm = LLM_CLASSES[llm_type](
        llm_name,
        base_url=base_url,
        api_key=api_key,
        model_max_length=model_max_length,
    )
    return llm


class ToolUse(BaseModel):
    id: Optional[str] = Field(
        default=None,
    )
    name: str = Field(
        ...,
        description="The name of the tool to call."
    )
    args: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The tool parameters and values in JSON object format."
    )

class ToolResult(BaseModel):
    id: Optional[str] = Field(
        default=None,
    )
    name: Optional[str] = Field(
        default=None,
        description="The name of the tool called."
    )
    response: Optional[Union[Dict, str]] = Field(
        default=None,
        description="The tool response in JSON object or string format."
    )

class Content(BaseModel):
    content: Union[str, ToolUse, ToolResult] = Field(
        default="",
        description="Content can be either text string or list of tool uses"
    )
    type: str = Field(
        ..., 
        description="Type of content", 
        enum=["text", "text_delta", "tool_use", "tool_result"]
    )
    stop_reason: str = Field(
        ...,
        description="Reason for stopping",
        enum=["end_turn", "max_tokens", "tool_use", "content_filter"],
    )


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    cached_output_tokens: int


class CacheConfig(BaseModel):
    name: str
    ttl: int


class Message(BaseModel):
    model: str
    created: int = Field(default_factory=lambda: int(time.time()))
    content: List[Content]
    usage: Usage = Field(default=None, description="Token usage of the model")
    role: str = Field(
        ..., 
        description="Role of the message", 
        enum=["user", "assistant", "system"]
    )
    cache_control: Optional[CacheConfig] = Field(
        default=None,
        description="Cache control for the message"
    )
