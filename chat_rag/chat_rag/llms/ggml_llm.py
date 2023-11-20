import os
from logging import getLogger
from typing import List, Dict

from huggingface_hub import hf_hub_download
from ctransformers import AutoModelForCausalLM, AutoConfig

from chat_rag.llms import RAGLLM


logger = getLogger(__name__)


def download_ggml_file(llm_name: str, ggml_model_filename: str, local_path: str):
    """
    Downloads the ggml model file from the huggingface hub.
    Parameters
    ----------
    llm_name : str
        The huggingface repo id.
    ggml_model_filename: str
        The filename of the model to load
    local_path: str
        The local path to save the model file to.
    Returns
    -------
    str
        The path to the downloaded model file.
    """
    logger.info(f"Downloading {ggml_model_filename} from {llm_name}...")
    return hf_hub_download(
        llm_name=llm_name,
        filename=ggml_model_filename,
        local_dir=local_path,
        local_dir_use_symlinks=True,
        token=os.environ["HUGGINGFACE_KEY"],
    )


class GGMLModel(RAGLLM):
    def __init__(self, llm_name: str, ggml_model_filename: str, model_config: str, **kwargs):
        """
        Initializes the ggml model. Optimized for CPU inference
        Parameters
        ----------
        llm_name : str
            The huggingface repo id.
        ggml_model_filename: str
            The filename of the model to load
        model_config: str
            The id of the model config to load
        """
        super().__init__(llm_name, **kwargs)
        local_path = os.path.abspath("models/")
        filename_path = os.path.join(local_path, ggml_model_filename)

        if not os.path.exists(filename_path):
            download_ggml_file(llm_name, ggml_model_filename, local_path)

        logger.info(f"Loading GGML {ggml_model_filename} from {filename_path}...")
        config = AutoConfig.from_pretrained(model_config)
        logger.info("Loaded model config")
        logger.info(config)
        self.model = AutoModelForCausalLM.from_pretrained(
            filename_path,
            config=config,
        )
        logger.info(f"Loaded GGML {ggml_model_filename} from {filename_path}!")

    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
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

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if (
            "threads" not in generation_config_dict
            or generation_config_dict["threads"] is None
        ):
            generation_config_dict["threads"] = os.cpu_count() // 2

        generation_config_dict["stop"] = stop_words

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        text = self.model(prompt, **generation_config_dict)
        return text

    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
    ) -> str:
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. Pair of (role, message).
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

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if(
            "threads" not in generation_config_dict
            or generation_config_dict["threads"] is None
        ):
            generation_config_dict["threads"] = os.cpu_count() // 2

        generation_config_dict["stop"] = stop_words

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        streamer = self.model(prompt, **generation_config_dict)  # returns a generator
        for word in streamer:
            yield word
