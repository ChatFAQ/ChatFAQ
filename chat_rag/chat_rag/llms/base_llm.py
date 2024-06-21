from typing import Dict, List, Optional

from pydantic import BaseModel


class LLM:

    def _check_tool_choice(self, tools: List[BaseModel], tool_choice: str) -> bool:
        """
        Adhere to the tool_choice parameter requirements.
        """
        if tool_choice:
            tool_choices = ["required", "auto"] + [tool.model_json_schema()['title'] for tool in tools]
            assert tool_choice in tool_choices, f"tool_choice must be one of {tool_choices}"
            

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
        tools: List[BaseModel] = None,
        tool_choice: str = None,
    ) -> Optional[str | List[str]]:
        pass

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[BaseModel] = None,
        tool_choice: str = None,
    ) -> Optional[str | List[str]]:
        pass
