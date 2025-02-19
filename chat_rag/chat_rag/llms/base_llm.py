from typing import Dict, List, Optional, Union, Tuple, Callable
from chat_rag.llms.types import Message


class LLM:

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        pass

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        pass
