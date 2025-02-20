from typing import Callable, Dict, List, Optional, Union

from chat_rag.llms.types import Message


class LLM:

    def stream(
        self,
        messages: List[Dict | Message],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    async def astream(
        self,
        messages: List[Dict | Message],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    def generate(
        self,
        messages: List[Dict | Message],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        pass

    async def agenerate(
        self,
        messages: List[Dict | Message],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[Callable, Dict]] = None,
        tool_choice: str = None,
    ) -> Message:
        pass

    def parse(
        self,
        messages: List[Dict | Message],
        schema: Dict,
    ) -> Dict:
        """
        Parse the response from the model into a structured format.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        schema : Dict
            The schema to use for the response. It must be a pydantic model json schema, it can be generated using the `model_json_schema` method of the pydantic model.
        Returns
        -------
        Dict
            The parsed message.
        """
        raise NotImplementedError("This LLM does not support enforced structured output or it has not been implemented.")

    async def aparse(
        self,
        messages: List[Dict | Message],
        schema: Dict,
    ) -> Dict:
        """
        Parse the response from the model into a structured format.
        """
        raise NotImplementedError("This LLM does not support enforced structured output or it has not been implemented.")
    
