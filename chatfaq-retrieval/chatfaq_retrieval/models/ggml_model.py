import os

from huggingface_hub import hf_hub_download
from ctransformers import AutoModelForCausalLM, AutoConfig


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
            self.download_ggml_file(repo_id, ggml_model_filename, local_path)


        config = AutoConfig.from_pretrained(model_config)
        self.model = AutoModelForCausalLM.from_pretrained(
            filename_path, 
            config=config,
        )

    def download_ggml_file(self, repo_id: str, ggml_model_filename: str, local_path: str):
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
        return hf_hub_download(
            repo_id=repo_id,
            filename=ggml_model_filename,
            local_dir=local_path,
            local_dir_use_symlinks=True,
        )


    def generate(self, prompt, seed=42, streaming=False, generation_kwargs: dict = None) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        prompt : str
            The prompt to generate text from.
        seed : int
            The seed to use for generation.
        streaming : bool
            Whether to use streaming generation.
        generation_kwargs : dict
            Keyword arguments for the generation.
        Returns
        -------
        str
            The generated text.
        """

        assert streaming == generation_kwargs['stream'], "Streaming must be set in generation_kwargs"

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if 'threads' not in generation_kwargs:
            generation_kwargs['threads'] = os.cpu_count() // 2


        if streaming:
            streamer = self.model(prompt, **generation_kwargs) # returns a generator
            for word in streamer:
                yield word
        else:
            text = self.model(prompt, **generation_kwargs)
            return text
            


