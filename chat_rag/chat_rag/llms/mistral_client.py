import os
from typing import Dict, List

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from chat_rag.llms import LLM


class MistralChatModel(LLM):
    def __init__(
        self,
        llm_name: str = "mistral-large-latest",
        **kwargs,
    ):
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.aclient = MistralAsyncClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
    ) -> List[ChatMessage]:
        """
        Formats the prompt to be used by the model into the correct Mistral format.
        """
        final_messages = [
            ChatMessage(role=message["role"], content=message["content"])
            for message in messages
        ]

        return final_messages

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
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

        messages = self.format_prompt(
            messages=messages,
        )

        for chunk in self.client.chat_stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

        return

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
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

        messages = self.format_prompt(
            messages=messages,
        )

        async for chunk in self.aclient.chat_stream(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

        return

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using a model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            messages=messages,
        )

        chat_response = self.client.chat(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        )

        return chat_response.choices[0].message.content

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using a model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            messages=messages,
        )

        chat_response = await self.aclient.chat(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            random_seed=seed,
        )

        return chat_response.choices[0].message.content
