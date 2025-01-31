import os
import time
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

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
    result: Optional[Union[Dict, str]] = Field(
        default=None,
        description="The tool result in JSON object or string format."
    )

class Content(BaseModel):
    text: Optional[str] = Field(
        default=None,
        description="Content can be either text string or list of tool uses"
    )
    tool_use: Optional[ToolUse] = Field(
        default=None,
        description="Tool use object"
    )
    tool_result: Optional[ToolResult] = Field(
        default=None,
        description="Tool result object"
    )
    type: str = Field(
        ..., 
        description="Type of content", 
        enum=["text", "text_delta", "tool_use", "tool_result"]
    )


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_creation_read_tokens: int


class CacheConfig(BaseModel):
    """
    Cache configuration for prompt caching. The name and ttl are only used by Gemini.
    """
    name: Optional[str] = Field(
        default=None,
        description="Name of the cache"
    )
    ttl: Optional[int] = Field(
        default=None,
        description="Time to live for the cache"
    )


class Message(BaseModel):
    created: int = Field(default_factory=lambda: int(time.time()))
    content: Union[List[Content], str]
    usage: Usage = Field(default=None, description="Token usage of the model")
    role: str = Field(
        ..., 
        description="Role of the message. 'model' is used by Gemini to indicate the model's response. 'developer' is used by OpenAI's o1 models" , 
        enum=["user", "assistant", "system", "model", "developer"]
    )
    cache_control: Optional[CacheConfig] = Field(
        default=None,
        description="Cache control for the message"
    )
    stop_reason: str = Field(
        ...,
        description="Reason for stopping",
        enum=["end_turn", "max_tokens", "tool_use", "content_filter"],
    )

    @field_validator('content')
    @classmethod
    def validate_content_structure(cls, v, info):
        if isinstance(v, str):
            return v
            
        for content in v:
            # Tool results can only be in user messages
            if content.tool_result and info.data.get('role') != 'user':
                raise ValueError("Tool results can only be included in user messages")
                
            # Tool uses can only be in assistant messages
            if content.tool_use and info.data.get('role') != 'assistant':
                raise ValueError("Tool uses can only be included in assistant messages")
                
            # System messages can only contain text
            if info.data.get('role') == 'system' and content.type != 'text':
                raise ValueError("System messages can only contain text content")
                
            # Validate that content type matches the actual content
            if content.type == 'text' and not content.text:
                raise ValueError("Text type content must include text")
            elif content.type == 'tool_use' and not content.tool_use:
                raise ValueError("Tool use type content must include tool_use data")
            elif content.type == 'tool_result' and not content.tool_result:
                raise ValueError("Tool result type content must include tool_result data")
        
        return v

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """
        Create a Message instance from a dictionary.
        
        Args:
            data (Dict): Dictionary containing message data
            
        Returns:
            Message: A new Message instance
        """
        # First create a basic instance without content validation
        instance = cls.model_construct(**data)
        
        # Now process the content with role already set as this is necessary for content validation
        if isinstance(data.get('content'), list):
            content_list = []
            for content_item in data['content']:
                content_list.append(Content(**content_item))
            instance.content = content_list
        else:
            instance.content = data.get('content')
            
        # Validate the complete instance
        return cls.model_validate(instance)

    class Config:
        validate_assignment = True
