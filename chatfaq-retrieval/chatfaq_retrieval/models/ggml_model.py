import os
from logging import getLogger
from typing import List

from huggingface_hub import hf_hub_download
from ctransformers import AutoModelForCausalLM, AutoConfig

logger = getLogger(__name__)


def download_ggml_file(repo_id: str, ggml_model_filename: str, local_path: str):
    """
    Downloads the ggml model file from the huggingface hub.
    Parameters
    ----------
    repo_id : str
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
    logger.info(f"Downloading {ggml_model_filename} from {repo_id}...")
    return hf_hub_download(
        repo_id=repo_id,
        filename=ggml_model_filename,
        local_dir=local_path,
        local_dir_use_symlinks=True,
    )


class GGMLModel:

    def __init__(self, repo_id: str, ggml_model_filename: str, model_config: str):
        """
        Initializes the ggml model. Optimized for CPU inference
        Parameters
        ----------
        repo_id : str
            The huggingface repo id.
        ggml_model_filename: str
            The filename of the model to load
        model_config: str
            The id of the model config to load
        """

        local_path = os.path.abspath("models/")
        filename_path = os.path.join(local_path, ggml_model_filename)

        if not os.path.exists(filename_path):
            download_ggml_file(repo_id, ggml_model_filename, local_path)

        logger.info(f"Loading GGML {ggml_model_filename} from {filename_path}...")
        config = AutoConfig.from_pretrained(model_config)
        logger.info("Loaded model config")
        logger.info(config)
        self.model = AutoModelForCausalLM.from_pretrained(
            filename_path,
            config=config,
        )
        logger.info(f"Loaded GGML {ggml_model_filename} from {filename_path}!")

    def generate(self, prompt, stop_words: List[str], generation_config_dict: dict = None) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        prompt : str
            The prompt to generate text from.
        stop_words : List[str]
            The stop words to use to stop generation.
        generation_config_dict : dict
            Keyword arguments for the generation.
        Returns
        -------
        str
            The generated text.
        """

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if 'threads' not in generation_config_dict or generation_config_dict['threads'] is None:
            generation_config_dict['threads'] = os.cpu_count() // 2
        
        generation_config_dict['stop'] = stop_words


        text = self.model(prompt, **generation_config_dict)
        return text
        
    def stream(self, prompt, stop_words: List[str], generation_config_dict: dict = None) -> str:
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        prompt : str
            The prompt to generate text from.
        stop_words : List[str]
            The stop words to use to stop generation.
        generation_config_dict : dict
            Keyword arguments for the generation.
        Returns
        -------
        str
            The generated text.
        """

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if 'threads' not in generation_config_dict or generation_config_dict['threads'] is None:
            generation_config_dict['threads'] = os.cpu_count() // 2
        
        generation_config_dict['stop'] = stop_words

        streamer = self.model(prompt, **generation_config_dict)  # returns a generator
        for word in streamer:
            yield word
        