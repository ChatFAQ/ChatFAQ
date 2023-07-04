from logging import getLogger
from typing import List

import pandas as pd

from chatfaq_retrieval.inf_retrieval.retriever import Retriever
from chatfaq_retrieval.models import GGMLModel, HFModel

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")


CONTEXT_PREFIX = {
    "en": "Context: ",
    "fr": "Contexte: ",
    "es": "Contexto: ",
}

QUESTION_PREFIX = {
    "en": "Question: ",
    "fr": "Question: ",
    "es": "Pregunta: ",
}


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
    RETRIEVER_MODEL = "intfloat/e5-small-v2"
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

        self.model = self.cached_models[repo_id]

    def format_prompt(
        self,
        query: str,
        contexts: List[str],
        system_prefix: str,
        system_tag: str,
        system_end: str,
        user_tag: str,
        user_end: str,
        assistant_tag: str,
        assistant_end: str,
        n_contexts_to_use: int = 3,
        lang: str = "en",
    ) -> str:
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

        if (
            system_tag == "" or system_tag is None
        ):  # To avoid adding the role_end tag if there is no system prefix
            prompt = f"{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{user_end}{assistant_tag}"
        else:
            prompt = f"{system_tag}{system_prefix}{system_end}{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{user_end}{assistant_tag}"

        return prompt

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
        prompt = self.format_prompt(
            text,
            contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        logger.info(f"Prompt: {prompt}")

        for new_text in self.model.stream(
            prompt, stop_words=stop_words, generation_config_dict=generation_config_dict
        ):
            yield {
                "res": new_text,
                "context": [
                    match[0]
                    for match in matches[
                    : prompt_structure_dict["n_contexts_to_use"]
                    ]
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
        prompt = self.format_prompt(
            text,
            contexts,
            **prompt_structure_dict,
            lang=lang,
        )

        logger.info(f"Prompt: {prompt}")

        output_text = self.model.generate(
            prompt, stop_words=stop_words, generation_config_dict=generation_config_dict
        )

        return {
            "res": output_text,
            "context": [
                match[0]
                for match in matches[: prompt_structure_dict["n_contexts_to_use"]]
            ],
        }
