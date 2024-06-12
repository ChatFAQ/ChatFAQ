import logging
import os
from typing import Dict, List

from transformers import AutoConfig, AutoTokenizer

from chat_rag.exceptions import (
    ModelNotFoundException,
    PromptTooLongException,
    RequestException,
)
from chat_rag.llms import OpenAIChatModel

logger = logging.getLogger(__name__)


class VLLMModel(OpenAIChatModel):
    """
    A client that sends requests to the VLLM server.
    """

    def __init__(
        self,
        llm_name: str,
        base_url: str = None,
        model_max_length: int = None,
        **kwargs,
    ):
        super().__init__(
            llm_name=llm_name, base_url=base_url, api_key="api_key",
        )  # vllm does not require an API key

        self._load_tokenizer(llm_name, model_max_length)

    def _load_tokenizer(self, llm_name, model_max_length):
        """
        We load the tokenizer of the model to be able to format the prompt to fit in the context length constraints.
        """
        hf_token = os.environ["HUGGINGFACE_KEY"]

        self.tokenizer = AutoTokenizer.from_pretrained(llm_name, token=hf_token)

        if model_max_length is not None:
            self.model_max_length = model_max_length
        else:
            self.config = AutoConfig.from_pretrained(llm_name, token=hf_token)
            self.model_max_length = (
                self.config.max_position_embeddings
                if self.config.max_position_embeddings is not None
                else self.tokenizer.model_max_length
            )

        self.has_chat_template = self.tokenizer.chat_template is not None
        print(f"Model max length: {self.model_max_length}")

    def _get_prompt_len(self, messages):
        prompt = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        return len(self.tokenizer.tokenize(prompt))

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """
        Formats the prompt to fit in the model's context length constraints.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. List of pairs (role, content).
        """

        n_messages_to_keep = len(messages)
        num_tokens = self._get_prompt_len(messages)
        margin = int(self.model_max_length * 0.1)

        system_prompt = None
        if messages[0]["role"] == "system":
            system_prompt = messages.pop(0)
            n_messages_to_keep -= 1  # don't count the system prompt

        while num_tokens > (self.model_max_length - margin):
            # When we reach the minimum number of contexts and messages and the prompt is still too long, we return None
            if n_messages_to_keep == 1:
                raise PromptTooLongException()

            n_messages_to_keep -= 1

            num_tokens = self._get_prompt_len(
                [system_prompt] + messages[-n_messages_to_keep:]
            )

        messages = messages[-n_messages_to_keep:]
        if system_prompt:
            messages = [system_prompt] + messages

        return messages

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """
        messages = self.format_prompt(messages)

        for chunk in super().stream(messages, temperature, max_tokens, seed):
            yield chunk

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """
        messages = self.format_prompt(messages)

        async for chunk in super().astream(messages, temperature, max_tokens, seed):
            yield chunk

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """
        messages = self.format_prompt(messages)

        return super().generate(messages, temperature, max_tokens, seed)

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        Returns
        -------
        str
            The generated text.
        """
        messages = self.format_prompt(messages)

        return await super().agenerate(messages, temperature, max_tokens, seed)


def return_openai_error(e):
    logger.error(f"Error with the request to the vLLM OpenAI server: {e}")
    if e.code == 400:  # BadRequestError
        raise PromptTooLongException()
    elif e.code == 404:  # NotFoundError
        raise ModelNotFoundException()
    else:
        logger.error(
            f"Error with the request to the vLLM OpenAI server: {e.body['message']}"
        )
        raise RequestException()
