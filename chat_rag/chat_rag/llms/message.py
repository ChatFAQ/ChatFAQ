from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
class ToolUse(BaseModel):
    id: str
    name: str
    input: Dict[str, Any]

class Content(BaseModel):
    text: str
    type: str = Field(..., description="Type of content", enum=["text", "tool_use"])
    tool_use: Optional[List[ToolUse]] = Field(default=None, description="List of tool uses if type is tool_use")
    stop_reason: str = Field(..., description="Reason for stopping", enum=["end_turn", "max_tokens", "tool_use", "content_filter"])

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int


class Message(BaseModel):
    role: str = Field(..., description="Role of the message", enum=["user", "assistant", "system"])
    content: List[Content]
    model: str
    created: int = Field(default_factory=lambda: int(time.time()))
    usage: Usage