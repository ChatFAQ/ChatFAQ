from typing import Dict, List, Optional, Union, Tuple, Callable
from chat_rag.llms.types import Message


class LLM:
    def _check_tool_choice(self, tools: List[Dict], tool_choice: str) -> str:
        """
        Adhere to the tool_choice parameter requirements.
        """

        if tool_choice:
            tool_choices = ["required", "auto"] + [
                tool["function"]["name"] for tool in tools
            ]
            assert tool_choice in tool_choices, (
                f"tool_choice must be one of {tool_choices}"
            )

        return tool_choice

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
