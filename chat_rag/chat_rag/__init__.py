import numpy as np
from logging import getLogger
from typing import List, Dict

import pandas as pd

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
        text,
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        
        contexts = self.retriever.retrieve([text], top_k=prompt_structure_dict["n_contexts_to_use"])
        contents = [context["content"] for context in contexts[0]]
        # log contexts except the 'content' column 
        for context in contexts[0]:
            for col in context:
                if col != "content":
                    logger.info(f"Contexts {col}: {context[col]}")

        for new_text in self.model.stream(
            text,
            contents,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=lang,
            stop_words=stop_words,
        ):
            yield {
                "res": new_text,
                "context": [
                    match
                    for match in contexts[: prompt_structure_dict["n_contexts_to_use"]]
                ],
            }

    def generate(
        self,
        text,
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        contexts = self.retriever.retrieve([text], top_k=prompt_structure_dict["n_contexts_to_use"])

        # log contexts except the 'content' column 
        for context in contexts:
            for col in context:
                if col != "content":
                    logger.info(f"Contexts {col}: {context[col]}")
        

        output_text = self.model.generate(
            text,
            contexts,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=lang,
            stop_words=stop_words,
        )

        return {
            "res": output_text,
            "context": [
                match[0]
                for match in contexts[: prompt_structure_dict["n_contexts_to_use"]]
            ],
        }
