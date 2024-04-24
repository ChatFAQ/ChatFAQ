import json
import os
from typing import Dict, Iterable, List, AsyncIterable

import aiohttp
import requests
from openai import OpenAI, AsyncOpenAI

from chat_rag.llms import RAGLLM
from chat_rag.exceptions import ModelNotFoundException, RequestException, PromptTooLongException

import logging

logger = logging.getLogger(__name__)


class VLLMModel(RAGLLM):
    """
    A client that sends requests to the VLLM server.
    """

    def __init__(
        self, llm_name: str, base_url: str = None, use_openai_api: bool = True, **kwargs
    ):
        super().__init__(llm_name=llm_name, **kwargs)
        if base_url is None:
            self.endpoint_url = os.environ["VLLM_ENDPOINT_URL"]
        else:
            self.endpoint_url = base_url

        self.llm_name = llm_name

        # I could use the already OpenAI implementation, but I prefer to implement the OpenAI API here also
        # because I need to do checks on the prompt length before sending it to the API
        # and I cannot do that on the OpenAI implementation
        if use_openai_api:
            self.client = OpenAI(
                base_url=self.endpoint_url
            )  # for VLLM OpenAI compatible API
        self.use_openai_api = use_openai_api
        print(f"Using vLLM OpenAI compatible API server: {self.use_openai_api}")

    def _format_prompt_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prefix: str,
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
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            lang=lang,
        )

        final_messages = [{"role": "system", "content": system_prompt}] + messages

        return final_messages

    def _generate_vllm(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        Generate text from a prompt using the vLLM API server.
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
        stop_words : List[str]
            The stop words to use to stop generation.
        Returns
        -------
        str
            The generated text.
        """

        prompt, _ = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "top_k": generation_config_dict["top_k"],
            "top_p": generation_config_dict["top_p"],
            "temperature": generation_config_dict["temperature"],
            "max_tokens": generation_config_dict["max_new_tokens"],
            "frequency_penalty": generation_config_dict["repetition_penalty"],
            "stop": stop_words,
            "stream": False,
        }

        response = requests.post(self.endpoint_url, json=pload, stream=False)

        if response.status_code != 200:
            logger.error(f"Error with the request to the vLLM server: {response.content}")
            raise RequestException()


        data = json.loads(response.content)

        # return the difference between the prompt and the output
        output = data["text"][0][len(prompt) :]

        if not output: # if there is an error vllm returns an empty string
            logger.error(f"Error with the request to the vLLM server.")
            raise RequestException()

        return output

    def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the vLLM OpenAI API.
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

        # Check how many messages and contexts we can fit in the model context length constraints
        _, (n_contexts, n_messages_to_keep) = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        messages = self._format_prompt_openai(
            messages=messages[:n_messages_to_keep],  # keep only the last n_messages_to_keep
            contexts=contexts[:n_contexts],  # keep only the last n_contexts
            **prompt_structure_dict,
            lang=lang,
        )

        try:
            print(f'LLM name: {self.llm_name}')
            response = self.client.chat.completions.create(
                model=self.llm_name,
                messages=messages,
                max_tokens=generation_config_dict["max_new_tokens"],
                temperature=generation_config_dict["temperature"],
                top_p=generation_config_dict["top_p"],
                presence_penalty=generation_config_dict["repetition_penalty"],
                seed=generation_config_dict["seed"],
                n=1,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return return_openai_error(e)

    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str | List[str] | None:
        """
        Generate text from a prompt using the model.
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
        stop_words : List[str]
            The stop words to use to stop generation.
        Returns
        -------
        str
            The generated text.
        """

        if self.use_openai_api:
            return self._generate_openai(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                **kwargs,
            )
        else:
            return self._generate_vllm(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                stop_words=stop_words,
                **kwargs,
            )

    def _stream_vllm(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> Iterable[str]:
        """
        Generate text from a prompt using the model.
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
        stop_words : List[str]
            The stop words to use to stop generation.
        Returns
        -------
        str
            The generated text.
        """

        prompt, _ = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "top_k": generation_config_dict["top_k"],
            "top_p": generation_config_dict["top_p"],
            "temperature": generation_config_dict["temperature"],
            "max_tokens": generation_config_dict["max_new_tokens"],
            "frequency_penalty": generation_config_dict["repetition_penalty"],
            "stop": stop_words,
            "stream": True,
        }

        response = requests.post(self.endpoint_url, json=pload, stream=True)

        prev_output = pload["prompt"]
        for n_token, chunk in enumerate(response.iter_lines(
            chunk_size=8192, decode_unicode=False, delimiter=b"\0"
        )):
            if n_token == 1 and not output: # if there is an error vllm returns an empty string as the second chunk (the first one is the prompt)
                raise RequestException()
            if chunk:
                data = json.loads(chunk.decode("utf-8"))
                if 'detail' in data:
                    logger.error(f"Error with the request to the vLLM server: {data['detail']}")
                    raise RequestException()
                output = data["text"]
                # yield the difference between the previous output and the current output
                output = output[0][len(prev_output) :]
                prev_output += output
                yield output

    def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> Iterable[str]:
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

        # Check how many messages and contexts we can fit in the model context length constraints
        _, (n_contexts, n_messages_to_keep) = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        messages = self._format_prompt_openai(
            messages=messages[:n_messages_to_keep],  # keep only the last n_messages_to_keep
            contexts=contexts[:n_contexts],  # keep only the last n_contexts
            **prompt_structure_dict,
            lang=lang,
        )

        try:

            response = self.client.chat.completions.create(
                model=self.llm_name,
                messages=messages,
                max_tokens=generation_config_dict["max_new_tokens"],
                temperature=generation_config_dict["temperature"],
                top_p=generation_config_dict["top_p"],
                presence_penalty=generation_config_dict["repetition_penalty"],
                seed=generation_config_dict["seed"],
                n=1,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    return
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[
                        0
                    ].delta.content  # return the delta text message

        except Exception as e:
            yield return_openai_error(e)
            return
            
    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str | Iterable[str] | None:
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. List of pairs (role, content)
        contexts : List[str]
            The contexts to use for generation.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.
        generation_config_dict : dict
            Keyword arguments for the generation.
        lang : str
            The language of the prompt.
        stop_words : List[str]
            The stop words to use to stop generation.
        Returns
        str
            The generated text.
        """

        if self.use_openai_api:
            for chunk in self._stream_openai(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                **kwargs,
            ):
                yield chunk
        else:
            for chunk in self._stream_vllm(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                stop_words=stop_words,
                **kwargs,
            ):
                yield chunk


class AsyncVLLMModel(RAGLLM):
    """
    A client that sends asynchronous requests to the VLLM server.
    """

    def __init__(
        self, llm_name: str, base_url: str = None, use_openai_api: bool = True, **kwargs
    ):
        super().__init__(llm_name=llm_name, **kwargs)
        if base_url is None:
            self.endpoint_url = os.environ["VLLM_ENDPOINT_URL"]
        else:
            self.endpoint_url = base_url

        self.llm_name = llm_name

        if use_openai_api:
            self.client = AsyncOpenAI(base_url=self.endpoint_url)  # for VLLM OpenAI compatible API
        self.use_openai_api = use_openai_api
        print(f"Using vLLM OpenAI compatible API server: {self.use_openai_api}")

    def _format_prompt_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        system_prefix: str,
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
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        system_prompt = self.format_system_prompt(
            contexts=contexts,
            system_prefix=system_prefix,
            lang=lang,
        )

        final_messages = [{"role": "system", "content": system_prompt}] + messages

        return final_messages


    async def _generate_vllm(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the vLLM API server.
        """
        prompt, _ = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "top_k": generation_config_dict["top_k"],
            "top_p": generation_config_dict["top_p"],
            "temperature": generation_config_dict["temperature"],
            "max_tokens": generation_config_dict["max_new_tokens"],
            "frequency_penalty": generation_config_dict["repetition_penalty"],
            "stop": stop_words,
            "stream": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint_url, json=pload) as response:
                if response.status != 200:
                    logger.error(
                        f"Error with the request to the vLLM server: {await response.text()}"
                    )
                    raise RequestException()

                data = await response.json()
                output = data["text"][0][len(prompt) :]

                if not output:  # if there is an error vllm returns an empty string
                    logger.error(f"Error with the request to the vLLM server.")
                    raise RequestException()

                return output

    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the vLLM OpenAI API.
        """
        _, (n_contexts, n_messages_to_keep) = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        messages = self._format_prompt_openai(
            messages=messages[:n_messages_to_keep],
            contexts=contexts[:n_contexts],
            **prompt_structure_dict,
            lang=lang,
        )

        try:
            print(f'LLM name: {self.llm_name}')
            response = await self.client.chat.completions.create(
                model=self.llm_name,
                messages=messages,
                max_tokens=generation_config_dict["max_new_tokens"],
                temperature=generation_config_dict["temperature"],
                top_p=generation_config_dict["top_p"],
                presence_penalty=generation_config_dict["repetition_penalty"],
                seed=generation_config_dict["seed"],
                n=1,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return return_openai_error(e)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str | None:
        """
        Generate text from a prompt using the model.
        """
        if self.use_openai_api:
            return await self._generate_openai(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                **kwargs,
            )
        else:
            return await self._generate_vllm(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                stop_words=stop_words,
                **kwargs,
            )

    async def _stream_vllm(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> AsyncIterable[str]:
        """
        Generate text from a prompt using the model.
        """
        prompt, _ = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "top_k": generation_config_dict["top_k"],
            "top_p": generation_config_dict["top_p"],
            "temperature": generation_config_dict["temperature"],
            "max_tokens": generation_config_dict["max_new_tokens"],
            "frequency_penalty": generation_config_dict["repetition_penalty"],
            "stop": stop_words,
            "stream": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint_url, json=pload, stream=True) as response:
                prev_output = pload["prompt"]
                async for n_token, chunk in enumerate(response.content.iter_chunks()):
                    if n_token == 1 and not output:  # if there is an error vllm returns an empty string as the second chunk (the first one is the prompt)
                        raise RequestException()
                    if chunk:
                        data = json.loads(chunk.decode("utf-8"))
                        if 'detail' in data:
                            logger.error(
                                f"Error with the request to the vLLM server: {data['detail']}"
                            )
                            raise RequestException()
                        output = data["text"]
                        output = output[0][len(prev_output) :]
                        prev_output += output
                        yield output

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> AsyncIterable[str]:
        """
        Generate text from a prompt using the model in streaming mode.
        """
        _, (n_contexts, n_messages_to_keep) = self.format_prompt(
            messages, contexts, **prompt_structure_dict, lang=lang
        )

        messages = self._format_prompt_openai(
            messages=messages[:n_messages_to_keep],
            contexts=contexts[:n_contexts],
            **prompt_structure_dict,
            lang=lang,
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.llm_name,
                messages=messages,
                max_tokens=generation_config_dict["max_new_tokens"],
                temperature=generation_config_dict["temperature"],
                top_p=generation_config_dict["top_p"],
                presence_penalty=generation_config_dict["repetition_penalty"],
                seed=generation_config_dict["seed"],
                n=1,
                stream=True,
            )
            async for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    return
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield return_openai_error(e)
            return

    async def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> AsyncIterable[str] | None:
        """
        Generate text from a prompt using the model in streaming mode.
        """
        if self.use_openai_api:
            async for chunk in self._stream_openai(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                **kwargs,
            ):
                yield chunk
        else:
            async for chunk in self._stream_vllm(
                messages=messages,
                contexts=contexts,
                prompt_structure_dict=prompt_structure_dict,
                generation_config_dict=generation_config_dict,
                lang=lang,
                stop_words=stop_words,
                **kwargs,
            ):
                yield chunk



    

def return_openai_error(e):
    logger.error(f"Error with the request to the vLLM OpenAI server: {e}")
    if e.code == 400: # BadRequestError
        raise PromptTooLongException()
    elif e.code == 404: # NotFoundError
        raise ModelNotFoundException()
    else:
        logger.error(f"Error with the request to the vLLM OpenAI server: {e.body['message']}")
        raise RequestException()