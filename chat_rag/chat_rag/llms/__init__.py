import os

from chat_rag.llms.base_llm import LLM
from chat_rag.llms.claude_client import ClaudeChatModel
from chat_rag.llms.format_tools import Mode, format_tools
from chat_rag.llms.gemini_client import GeminiChatModel
from chat_rag.llms.mistral_client import MistralChatModel
from chat_rag.llms.openai_client import OpenAIChatModel
from chat_rag.llms.together_client import TogetherChatModel
from chat_rag.llms.types import (
    CacheConfig,
    Content,
    Message,
    ToolResult,
    ToolUse,
    Usage,
)
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
    "Message",
    "CacheConfig",
    "Usage",
    "Content",
    "ToolResult",
    "ToolUse",
    "TogetherChatModel",
]


LLM_CLASSES = {
    "claude": ClaudeChatModel,
    "mistral": MistralChatModel,
    "openai": OpenAIChatModel,
    "vllm": VLLMModel,
    "together": TogetherChatModel,
    "gemini": GeminiChatModel,
}

def load_llm(llm_type: str, llm_name: str, base_url: str = None, model_max_length: int = None, api_key: str = None) -> LLM:

    llm = LLM_CLASSES[llm_type](
        llm_name,
        base_url=base_url,
        api_key=api_key,
        model_max_length=model_max_length,
    )
    return llm