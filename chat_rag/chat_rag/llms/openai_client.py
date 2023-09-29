from typing import List, Dict
import os

import openai

from chat_rag.llms import BaseLLM


CONTEXT_PREFIX = {
    "en": "Given the following contexts: ",
    "fr": "Étant donné les contextes suivants: ",
    "es": "Dados los siguientes contextos: ",
}

QUESTION_PREFIX = {
    "en": "Answer the next question: ",
    "fr": "Répondez à la question suivante: ",
    "es": "Responde la siguiente pregunta: ",
}


class OpenAIModel(BaseLLM):
    def __init__(
        self,
        llm_name: str,
        **kwargs,
    ):
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.llm_name = llm_name

    def format_prompt(
        self,
        query: str,
        contexts: List[str],
        system_prefix: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Formats the prompt to be used by the model.
        Parameters
        ----------
        query : str
            The query to answer.
        contexts : list
            The context to use.
        system_prefix : str
            The prefix to indicate instructions for the LLM.
        system_tag : str
            The tag to indicate the start of the system prefix for the LLM.
        system_end : str
            The tag to indicate the end of the system prefix for the LLM.
        user_tag : str
            The tag to indicate the start of the user input.
        user_end : str
            The tag to indicate the end of the user input.
        assistant_tag : str
            The tag to indicate the start of the assistant output.
        assistant_end : str
            The tag to indicate the end of the assistant output.
            The tag to indicate the end of the role (system role, user role, assistant role).
        n_contexts_to_use : int, optional
            The number of contexts to use, by default 3
        lang : str, optional
            The language of the prompt, by default 'en'
        """
        contexts_prompt = CONTEXT_PREFIX[lang]
        for context in contexts[:n_contexts_to_use]:
            contexts_prompt += f"{context}\n"

        return [
            {"role": "system", "content": system_prefix},
            {
                "role": "user",
                "content": f"{contexts_prompt}{QUESTION_PREFIX[lang]}{query}",
            },
        ]

    def generate(
        self,
        query,
        contexts,
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
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
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            query=query,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        response = openai.ChatCompletion.create(
            model=self.llm_name,
            messages=messages,
            max_tokens=generation_config_dict["max_new_tokens"],
            temperature=generation_config_dict["temperature"],
            top_p=generation_config_dict["top_p"],
            presence_penalty=generation_config_dict["repetition_penalty"],
            n=1,
            stream=False,
        )
        return response.choices[0]["message"]["content"]

    def stream(
        self,
        query,
        contexts,
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model in streaming mode.
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
        Returns
        -------
        str
            The generated text.
        """

        messages = self.format_prompt(
            query=query,
            contexts=contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        response = openai.ChatCompletion.create(
            model=self.llm_name,
            messages=messages,
            max_tokens=generation_config_dict["max_new_tokens"],
            temperature=generation_config_dict["temperature"],
            top_p=generation_config_dict["top_p"],
            presence_penalty=generation_config_dict["repetition_penalty"],
            n=1,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0]["finish_reason"] == "stop":
                return
            elif "content" in chunk.choices[0]["delta"]:  # if contains new text
                yield chunk.choices[0]["delta"]["content"]
