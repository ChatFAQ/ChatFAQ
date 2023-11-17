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
        prev_contents: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        
        # Retrieve
        contexts = self.retriever.retrieve([messages[-1]['content']], top_k=prompt_structure_dict["n_contexts_to_use"])[0] # retrieve contexts
        contents = [context["content"] for context in contexts] # get unique contexts
        returned_contexts = [contexts[:prompt_structure_dict["n_contexts_to_use"]]] # structure for references
        contents = list(set(contents + prev_contents))

        # Generate
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
        prev_contents: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        
        # Retrieve
        contexts = self.retriever.retrieve([messages[-1]['content']], top_k=prompt_structure_dict["n_contexts_to_use"])[0] # retrieve contexts
        contents = [context["content"] for context in contexts] # get unique contexts
        returned_contexts = [contexts[:prompt_structure_dict["n_contexts_to_use"]]] # structure for references
        contents = list(set(contents + prev_contents))
        

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
            "context": returned_contexts,
        }
