import json
from typing import Iterable, List
import os

import requests

from chatfaq_retrieval.models import BaseModel

class VLLModel(BaseModel):
    """
    A client that sends requests to the VLLM server.
    """
    def __init__(self):
        super().__init__()
        self.endpoint_url = os.environ["VLLM_ENDPOINT_URL"]

    def generate(
        self,
        query,
        contexts,
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> List[str]:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        query : str
            The query to generate text from.
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

        prompt = self.format_prompt(query, contexts, **prompt_structure_dict, lang=lang)

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

        data = json.loads(response.content)

        return data["text"]
    
    def stream(
        self,
        query,
        contexts,
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
        query : str
            The query to generate text from.
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

        prompt = self.format_prompt(query, contexts, **prompt_structure_dict, lang=lang)

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

        for chunk in response.iter_lines(chunk_size=8192,
                                 decode_unicode=False,
                                 delimiter=b"\0"):
            if chunk:
                data = json.loads(chunk.decode("utf-8"))
                output = data["text"]
                yield output
