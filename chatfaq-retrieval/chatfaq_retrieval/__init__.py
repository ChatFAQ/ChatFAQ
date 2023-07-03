import time
from logging import getLogger
from threading import Thread

import pandas as pd
import torch

from chatfaq_retrieval.inf_retrieval.retriever import Retriever
from transformers import T5Tokenizer, T5ForConditionalGeneration, TextIteratorStreamer

from chatfaq_retrieval.models import GGMLModel, HFModel

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")


def get_model(
    repo_id: str,
    ggml_model_filename: str = None,
    use_cpu: bool = False,
    model_config: str = None,
    huggingface_auth_token: str = None,
    load_in_8bit: bool = False,
    trust_remote_code_tokenizer: bool = False,
    trust_remote_code_model: bool = False,
    revision: str = "main",    
):
    """
    Returns an instance of the corresponding Answer Generator Model.
    Parameters
    ----------
    repo_id: str
        The huggingface repo id which contains the model to load
    ggml_model_filename: str
        The filename of the model to load if using a ggml model
    use_cpu: bool
        Whether to use cpu or gpu
    model_config: str
        The filename of the model config to load if using a ggml model
    huggingface_auth_token: str
        The huggingface auth token to use when loading the model
    load_in_8bit: bool
        Whether to load the model in 8bit mode
    trust_remote_code_tokenizer: bool
        Whether to trust the remote code when loading the tokenizer
    trust_remote_code_model: bool
        Whether to trust the remote code when loading the model
    revision: str
        The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
    Returns
    -------
    model:
        A Transformers Model or GGML Model (using CTransformers), depending on the model_id.
    """

    if ggml_model_filename is not None:  # Need to load the ggml model file
        return GGMLModel(
            repo_id,
            ggml_model_filename,
            use_cpu=use_cpu,
            model_config=model_config,
        )
    else:
        return HFModel(
            repo_id,
            use_cpu=use_cpu,
            huggingface_auth_token=huggingface_auth_token,
            load_in_8bit=load_in_8bit,
            trust_remote_code_tokenizer=trust_remote_code_tokenizer,
            trust_remote_code_model=trust_remote_code_model,
            revision=revision,
        )


class RetrieverAnswerer:
    RETRIEVER_MODEL = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    MAX_GPU_MEM = "18GiB"
    MAX_CPU_MEM = "12GiB"
    cached_tokenizers = {}
    cached_models = {}

    def __init__(
        self,
        base_data: str,
        repo_id: str,
        context_col: str,
        embedding_col: str,
        ggml_model_filename: str = None,
        use_cpu: bool = False,
        model_config: str = None,
        huggingface_auth_token: str = None,
        load_in_8bit: bool = False,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        revision: str = "main",
    ):
        self.use_cpu = use_cpu
        # --- Set Up Retriever ---

        # self.prompt_gen = PromptGenerator()
        self.retriever = Retriever(
            pd.read_csv(base_data),
            model_name=self.RETRIEVER_MODEL,
            context_col=context_col,
            use_cpu=use_cpu,
        )

        self.retriever.build_embeddings(embedding_col=embedding_col)

        if repo_id not in self.cached_models:
            self.cached_models[repo_id] = get_model(
                repo_id,
                ggml_model_filename=ggml_model_filename,
                use_cpu=use_cpu,
                model_config=model_config,
                huggingface_auth_token=huggingface_auth_token,
                load_in_8bit=load_in_8bit,
                trust_remote_code_tokenizer=trust_remote_code_tokenizer,
                trust_remote_code_model=trust_remote_code_model,
                revision=revision,
            )

    def query(self, text, seed=42, streaming=False):
        matches = self.retriever.get_top_matches(text, top_k=5)
        contexts = self.retriever.get_contexts(matches)
        prompt, n_of_contexts = self.prompt_gen.create_prompt(
            text, contexts, lang="en1", max_length=512
        )

        if streaming:
            for new_text in self.model.generate(prompt, streaming=True, seed=seed):
                yield {
                    "res": new_text,
                    "context": [match[0] for match in matches[:n_of_contexts]],
                }
        else:
            output_text = self.model.generate(prompt, streaming=False, seed=seed)

            return {
                "res": output_text,
                "context": [match[0] for match in matches[:n_of_contexts]],
            }
