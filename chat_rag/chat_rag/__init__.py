import numpy as np
from logging import getLogger
from typing import List, Dict

import pandas as pd

from chat_rag.inf_retrieval.retriever import Retriever
from chat_rag.llms import BaseLLM

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")


class RetrieverAnswerer:
    MAX_GPU_MEM = "18GiB"
    MAX_CPU_MEM = "12GiB"
    cached_tokenizers = {}
    cached_models = {}

    def __init__(
        self,
        data: Dict[str, List[str]],
        embeddings: List[np.ndarray],
        llm_model: BaseLLM,
        llm_name: str,
        use_cpu: bool = False,
        retriever_model: str = "intfloat/e5-small-v2",
        huggingface_key: str = None,
    ):
        self.use_cpu = use_cpu
        # --- Set Up Retriever ---

        self.retriever = Retriever(
            data=data,
            embeddings=embeddings,
            model_name=retriever_model,
            use_cpu=use_cpu,
            huggingface_key=huggingface_key,
        )

        if llm_model not in self.cached_models:
            self.cached_models[llm_name] = llm_model

        self.model = self.cached_models[llm_name]

    def stream(
        self,
        text,
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        matches = self.retriever.get_top_matches(text, top_k=prompt_structure_dict["n_contexts_to_use"])
        contexts = self.retriever.get_contexts(matches)

        # log contexts except the 'content' column 
        for match, context in zip(matches, contexts):
            logger.info(f"Match: {match}")
            for col in context:
                if col != "content":
                    logger.info(f"Contexts {col}: {context[col]}")

        for new_text in self.model.stream(
            text,
            contexts,
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
        matches = self.retriever.get_top_matches(text, top_k=prompt_structure_dict["n_contexts_to_use"])
        contexts = self.retriever.get_contexts(matches)

        # log contexts except the 'content' column 
        for match, context in zip(matches, contexts):
            logger.info(f"Match: {match}")
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
                for match in matches[: prompt_structure_dict["n_contexts_to_use"]]
            ],
        }
