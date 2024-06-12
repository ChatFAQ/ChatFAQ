import os
from typing import Dict, List

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from chat_rag.llms import LLM


class MistralChatModel(LLM):
    def __init__(
        self,
        llm_name: str,
        base_url: str = None,
        **kwargs,
    ):
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prompt: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : list
            The context to use.
        system_prompt : str
            The prefix to indicate instructions for the LLM.
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prompt=system_prompt,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )
        final_messages = [ChatMessage(role='system', content=system_prompt)]  \
            + [ChatMessage(role=message['role'], content=message['content']) for message in messages]
        
        print(final_messages)

        return final_messages
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ---------text-
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        chat_response = self.client.chat(
            model=self.llm_name,
            messages=messages,
            temperature=generation_config_dict["temperature"],
            top_p=generation_config_dict["top_p"],
            max_tokens=generation_config_dict["max_new_tokens"],
            random_seed=generation_config_dict["seed"],
        )

        return chat_response.choices[0].message.content

    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        for chunk in self.client.chat_stream(
            model=self.llm_name,
            messages=messages,
            temperature=generation_config_dict["temperature"],
            top_p=generation_config_dict["top_p"],
            max_tokens=generation_config_dict["max_new_tokens"],
            random_seed=generation_config_dict["seed"],
        ):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

        return


class AsyncMistralChatModel(LLM):
    def __init__(
        self,
        llm_name: str,
        **kwargs,
    ):
        self.client = MistralAsyncClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.llm_name = llm_name

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prompt: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : list
            The context to use.
        system_prompt : str
            The prefix to indicate instructions for the LLM.
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prompt=system_prompt,
            n_contexts_to_use=n_contexts_to_use,
            lang=lang,
        )
        final_messages = [ChatMessage(role='system', content=system_prompt)]  \
            + [ChatMessage(role=message['role'], content=message['content']) for message in messages]
        
        print(final_messages)

        return final_messages
  

    async def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ---------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            messages=messages,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        chat_response = await self.client.chat(
            model=self.llm_name,
            messages=messages,
            temperature=generation_config_dict["temperature"],
            top_p=generation_config_dict["top_p"],
            max_tokens=generation_config_dict["max_new_tokens"],
            random_seed=generation_config_dict["seed"],
        )

        return chat_response.choices[0].message.content

    async def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
            """
            Generate text from a prompt using the model in streaming mode.
            Parameters
            ---------
            messages : List[Tuple[str, str]]
                The messages to use for the prompt. Pair of (role, message).
            contexts : List[str]
                The contexts to use for generation.
            prompt_structure_dict : dict
                Dictionary containing the structure of the prompt.
            generation_config_dict : dict
                Keyword arguments for the generation.
            lang : str
                The language of the prompt.
            Returns
            -------
            str
                The generated text.
            """
            
            messages = self.format_prompt(
                messages=messages,
                contexts=contexts,
                **prompt_structure_dict,
                lang=lang,
            )
    
            async for chunk in self.client.chat_stream(
                model=self.llm_name,
                messages=messages,
                temperature=generation_config_dict["temperature"],
                top_p=generation_config_dict["top_p"],
                max_tokens=generation_config_dict["max_new_tokens"],
                random_seed=generation_config_dict["seed"],
            ):
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
    
            return