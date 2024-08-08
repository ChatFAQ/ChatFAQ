from typing import Dict, List, Optional, Union, Tuple

from pydantic import BaseModel


class LLM:

    def _check_tool_choice(self, tools: List[Union[BaseModel, Dict]], tool_choice: str) -> Tuple[Dict, str]:
        """
        Adhere to the tool_choice parameter requirements.
        """
        if isinstance(tools[0], BaseModel):
            tools = [tool.model_json_schema() for tool in tools]

        if tool_choice:
            tool_choices = ["required", "auto"] + [tool['title'] for tool in tools]
            assert tool_choice in tool_choices, f"tool_choice must be one of {tool_choices}"

        return tools, tool_choice
            

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
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ) -> Optional[str | List[str]]:
        pass

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ) -> Optional[str | List[str]]:
        pass