import time
from logging import getLogger
from threading import Thread

import pandas as pd
import torch

from chatfaq_retrieval.inf_retrieval.retriever import Retriever
from chatfaq_retrieval.prompt_generator.prompt_generator import PromptGenerator
from transformers import T5Tokenizer, T5ForConditionalGeneration, TextIteratorStreamer

from models import GGMLModel, HFModel

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")

def get_model(repo_id: str, model_filename: str = None, use_cpu: bool = False, model_config: str = None, tokenizer_kwargs: dict = None, model_kwargs: dict = None):
    """
    Returns an instance of the corresponding Answer Generator Model.
    Parameters
    ----------
    repo_id: str
        The huggingface repo id which contains the model to load
    model_filename: str
        The filename of the model to load if using a ggml model
    use_cpu: bool
        Whether to use cpu or gpu
    model_config: str
        The filename of the model config to load if using a ggml model
    tokenizer_kwargs: dict
        Keyword arguments for the tokenizer
    model_kwargs: dict
        Keyword arguments for the model
    Returns
    -------
    model:
        A Transformers Model or GGML Model (using CTransformers), depending on the model_id.
    """

    if model_filename is not None: # Need to load the ggml model file
        return GGMLModel(repo_id, model_filename, use_cpu=use_cpu, model_config=model_config, model_kwargs=model_kwargs)
    else:
        return HFModel(repo_id, use_cpu=use_cpu, tokenizer_kwargs=tokenizer_kwargs, model_kwargs=model_kwargs)    


class RetrieverAnswerer:
    RETRIEVER_MODEL = 'sentence-transformers/multi-qa-MiniLM-L6-cos-v1'
    MAX_GPU_MEM = "18GiB"
    MAX_CPU_MEM = '12GiB'
    cached_tokenizers = {}
    cached_models = {}

    def __init__(self, base_data: str, repo_id: str, context_col: str, embedding_col: str, model_filename: str = None, use_cpu: bool = False, model_config: str = None, tokenizer_kwargs: dict = None, model_kwargs: dict = None):
        self.use_cpu = use_cpu
        # --- Set Up Retriever ---

        self.prompt_gen = PromptGenerator()
        self.retriever = Retriever(
            pd.read_csv(base_data),
            model_name=self.RETRIEVER_MODEL,
            context_col=context_col,
            use_cpu=use_cpu
        )

        self.retriever.build_embeddings(embedding_col=embedding_col)

        if repo_id not in self.cached_models:
            self.cached_models[repo_id] = get_model(repo_id, model_filename=model_filename, use_cpu=use_cpu, model_config=model_config, tokenizer_kwargs=tokenizer_kwargs, model_kwargs=model_kwargs)

    def query(self, text, seed=42, streaming=False):

        matches = self.retriever.get_top_matches(text, top_k=5)
        contexts = self.retriever.get_contexts(matches)
        prompt, n_of_contexts = self.prompt_gen.create_prompt(text, contexts, lang='en1', max_length=512)


        if streaming:
            for new_text in self.model.generate(prompt, streaming=True, seed=seed):
                yield {
                    "res": new_text,
                    "context": [match[0] for match in matches[:n_of_contexts]]
                }
        else:
            output_text = self.model.generate(prompt, streaming=False, seed=seed)

            return {
                "res": output_text,
                "context": [match[0] for match in matches[:n_of_contexts]]
            }

