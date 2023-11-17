import numpy as np
from logging import getLogger
from typing import List, Dict

from chat_rag.llms import RAGLLM

logger = getLogger(__name__)


class RAG:
    """
    Class for generating responses using the Retrieval-Augmented Generation (RAG) pattern.
    """
    def __init__(
        self,
        retriever,
        llm_model: RAGLLM,
    ):
        
        self.retriever = retriever
        self.model = llm_model

    def stream(
        self,
        messages: List[Dict[str, str]],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        
        queries = [message['content'] for message in messages if message['role'] == 'user']
        contexts_list = self.retriever.retrieve(queries, top_k=prompt_structure_dict["n_contexts_to_use"])
        contents = list(set([context["content"] for contexts in contexts_list for context in contexts]))

        returned_contexts = [contexts_list[-1][:prompt_structure_dict["n_contexts_to_use"]]]

        for new_text in self.model.stream(
            messages,
            contents,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=lang,
            stop_words=stop_words,
        ):
            yield {
                "res": new_text,
                "context": returned_contexts,
            }

    def generate(
        self,
        messages: List[Dict[str, str]],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        
        queries = [message['content'] for message in messages if message['role'] == 'user']
        contexts_list = self.retriever.retrieve(queries, top_k=prompt_structure_dict["n_contexts_to_use"])
        contents = list(set([context["content"] for contexts in contexts_list for context in contexts]))
        

        output_text = self.model.generate(
            messages,
            contents,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=lang,
            stop_words=stop_words,
        )

        return {
            "res": output_text,
            "context": contexts_list[-1][:prompt_structure_dict["n_contexts_to_use"]],
        }
