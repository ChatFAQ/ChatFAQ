from logging import getLogger
from typing import List

import pandas as pd

from chatfaq_retrieval.inf_retrieval.retriever import Retriever
from chatfaq_retrieval.models import GGMLModel, HFModel, OpenAIModel

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")


def get_model(
    llm_name: str,
    llm_type: str,
    ggml_model_filename: str = None,
    use_cpu: bool = False,
    model_config: str = None,
    load_in_8bit: bool = False,
    use_fast_tokenizer: bool = True,
    trust_remote_code_tokenizer: bool = False,
    trust_remote_code_model: bool = False,
    revision: str = "main",
):
    """
    Returns an instance of the corresponding Answer Generator Model.
    Parameters
    ----------
    llm_name: str
        The model id, it could be a hugginface repo id, a ggml repo id, or an openai model id.
    llm_type: str
        The type of LLM to use.
    ggml_model_filename: str
        The filename of the model to load if using a ggml model
    use_cpu: bool
        Whether to use cpu or gpu
    model_config: str
        The filename of the model config to load if using a ggml model
    load_in_8bit: bool
        Whether to load the model in 8bit mode
    use_fast_tokenizer: bool
        Whether to use the fast tokenizer
    trust_remote_code_tokenizer: bool
        Whether to trust the remote code when loading the tokenizer
    trust_remote_code_model: bool
        Whether to trust the remote code when loading the model
    revision: str
        The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
    Returns
    -------
    model:
        A Transformers Model, GGML Model (using CTransformers) or OpenAI Model depending on the llm_name.
    """

    if llm_name.startswith("gpt-3.5") or llm_name.startswith("gpt-4"):
        return OpenAIModel(
            llm_name,
        )

    elif ggml_model_filename is not None:  # Need to load the ggml model file
        return GGMLModel(
            llm_name,
            ggml_model_filename,
            model_config=model_config,
        )

    else:
        return HFModel(
            llm_name,
            use_cpu=use_cpu,
            load_in_8bit=load_in_8bit,
            use_fast_tokenizer=use_fast_tokenizer,
            trust_remote_code_tokenizer=trust_remote_code_tokenizer,
            trust_remote_code_model=trust_remote_code_model,
            revision=revision,
        )


class RetrieverAnswerer:
    RETRIEVER_MODEL = "intfloat/e5-small-v2"
    MAX_GPU_MEM = "18GiB"
    MAX_CPU_MEM = "12GiB"
    cached_tokenizers = {}
    cached_models = {}

    def __init__(
        self,
        base_data: str,
        llm_name: str,
        llm_type: str,
        context_col: str,
        embedding_col: str,
        ggml_model_filename: str = None,
        use_cpu: bool = False,
        model_config: str = None,
        auth_token: str = None,
        load_in_8bit: bool = False,
        use_fast_tokenizer: bool = True,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        revision: str = "main",
    ):
        self.use_cpu = use_cpu
        # --- Set Up Retriever ---

        self.retriever = Retriever(
            pd.read_csv(base_data),
            model_name=self.RETRIEVER_MODEL,
            context_col=context_col,
            use_cpu=use_cpu,
        )

        self.retriever.build_embeddings(embedding_col=embedding_col)

        if llm_name not in self.cached_models:
            self.cached_models[llm_name] = get_model(
                llm_name,
                ggml_model_filename=ggml_model_filename,
                use_cpu=use_cpu,
                model_config=model_config,
                auth_token=auth_token,
                load_in_8bit=load_in_8bit,
                use_fast_tokenizer=use_fast_tokenizer,
                trust_remote_code_tokenizer=trust_remote_code_tokenizer,
                trust_remote_code_model=trust_remote_code_model,
                revision=revision,
            )

        self.model = self.cached_models[llm_name]

    def stream(
        self,
        text,
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
        lang: str = "en",
    ):
        matches = self.retriever.get_top_matches(text, top_k=5)
        contexts = self.retriever.get_contexts(matches)

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
                    match[0]
                    for match in matches[: prompt_structure_dict["n_contexts_to_use"]]
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
        matches = self.retriever.get_top_matches(text, top_k=5)
        contexts = self.retriever.get_contexts(matches)

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
