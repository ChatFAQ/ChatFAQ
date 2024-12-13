import logging
import os
from typing import Dict, List, Union

from pydantic import BaseModel

from chat_rag.exceptions import (
    ModelNotFoundException,
    PromptTooLongException,
    RequestException,
)
from chat_rag.llms import OpenAIChatModel

# Check if transformers is installed
HAS_TRANSFORMERS = False
try:
    from transformers import AutoConfig, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    pass

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

        if HAS_TRANSFORMERS:
            self._load_tokenizer(llm_name, model_max_length)

    def _load_tokenizer(self, llm_name, model_max_length):
        """
        We load the tokenizer of the model to be able to format the prompt to fit in the context length constraints.
        """
        hf_token = os.getenv("HUGGINGFACE_KEY", None)

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

        if HAS_TRANSFORMERS:
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
        if HAS_TRANSFORMERS:
            messages = self.format_prompt(messages)

        async for chunk in super().astream(messages, temperature, max_tokens, seed):
            yield chunk

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
        json_schema: Dict = None,
        ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        tools : List[Union[BaseModel, Dict]], optional
            Tools for function calling. Cannot be used with json_schema.
        tool_choice : str, optional
            The tool choice to use for tool use.
        json_schema : Dict, optional
            JSON schema to guide the generation format. Cannot be used with tools.
        """
        if tools and json_schema:
            raise ValueError("Cannot use both tools and json_schema at the same time")

        if HAS_TRANSFORMERS:
            messages = self.format_prompt(messages)

        # Handle tools and json_schema kwargs
        extra_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            extra_kwargs.update({"tools": tools, "tool_choice": tool_choice})
        elif json_schema:
            extra_kwargs["extra_body"] = {"guided_json": json_schema}

        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=False,
            **extra_kwargs,
        )

        message = response.choices[0].message
        if message.tool_calls:
            return self._extract_tool_info(message)

        return message.content

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
        json_schema: Dict = None,
    ):
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        tools : List[Union[BaseModel, Dict]], optional
            Tools for function calling. Cannot be used with json_schema.
        tool_choice : str, optional
            The tool choice to use for tool use.
        json_schema : Dict, optional
            JSON schema to guide the generation format. Cannot be used with tools.
        """
        if tools and json_schema:
            raise ValueError("Cannot use both tools and json_schema at the same time")

        if HAS_TRANSFORMERS:
            messages = self.format_prompt(messages)

        # Handle tools and json_schema kwargs
        extra_kwargs = {}
        if tools:
            tools, tool_choice = self._format_tools(tools, tool_choice)
            extra_kwargs.update({"tools": tools, "tool_choice": tool_choice})
        elif json_schema:
            extra_kwargs["extra_body"] = {"guided_json": json_schema}

        response = await self.aclient.chat.completions.create(
            model=self.llm_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            n=1,
            stream=False,
            **extra_kwargs,
        )

        message = response.choices[0].message
        if message.tool_calls:
            return self._extract_tool_info(message)
        
        return message.content

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