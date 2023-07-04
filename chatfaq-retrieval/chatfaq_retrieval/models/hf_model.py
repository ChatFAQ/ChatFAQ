from threading import Thread
from logging import getLogger
from typing import List

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
    T5Tokenizer,
    T5ForConditionalGeneration,
)

logger = getLogger(__name__)


class HFModel:
    MAX_GPU_MEM = "18GiB"  # Why this
    MAX_CPU_MEM = "12GiB"

    def __init__(
        self,
        repo_id: str,
        use_cpu: bool,
        huggingface_auth_token: str = None,
        load_in_8bit: bool = False,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        revision: str = "main",
    ):
        """
        Initializes the model and tokenizer.
        Parameters
        ----------
        repo_id : str
            The huggingface repo id.
        use_cpu : bool
            Whether to use cpu or gpu.
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
        """
        self.use_cpu = use_cpu
        ######### JUST FOR TESTING #########
        if "t5" in repo_id:
            logger.info(f"Loading T5 model from {repo_id}...")
            self.tokenizer, self.model = self.get_t5(repo_id)

        else:
            device_map = (
                "auto" if (not use_cpu and torch.cuda.is_available()) else None
            )  # use gpu if available
            self.device = (
                "cuda:0" if (not use_cpu and torch.cuda.is_available()) else None
            )  # For moving tensors to the GPU
            memory_device = {"cpu": self.MAX_CPU_MEM}
            if not use_cpu and torch.cuda.is_available():
                memory_device = {0: self.MAX_GPU_MEM}

            logger.info(f"Loading HF model from {repo_id}...")
            self.tokenizer = AutoTokenizer.from_pretrained(repo_id, use_auth_token=huggingface_auth_token,
                                                           revision=revision,
                                                           trust_remote_code=trust_remote_code_tokenizer)
            self.model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                device_map=device_map,
                torch_dtype="auto",
                max_memory=memory_device,
                low_cpu_mem_usage=True,
                use_auth_token=huggingface_auth_token,
                revision=revision,
                trust_remote_code=trust_remote_code_model,
            )
            self.streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True, skip_prompt=True)

    def get_t5(self, repo_id):
        ######### JUST FOR TESTING #########
        tokenizer = T5Tokenizer.from_pretrained(repo_id)

        device_map = (
            "auto" if (not self.use_cpu and torch.cuda.is_available()) else None
        )  # use gpu if available
        memory_device = {"cpu": self.MAX_CPU_MEM}
        dtype = torch.float32  # much faster for cpu, but consumes more memory
        if not self.use_cpu and torch.cuda.is_available():
            memory_device = {0: self.MAX_GPU_MEM}
            dtype = torch.bfloat16

        return tokenizer, T5ForConditionalGeneration.from_pretrained(
            repo_id, device_map=device_map, torch_dtype=dtype, max_memory=memory_device
        )

    def generate(
        self, prompt, stop_words: List[str], generation_config_dict: dict = None
    ) -> str:
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
        torch.manual_seed(generation_config_dict['seed'])

        generation_config_dict.pop("seed")

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )

        generation_config_dict = dict(
                input_ids=input_ids,
                do_sample=True,
                **generation_config_dict,
            )

        with torch.inference_mode():
            outputs = self.model.generate(**generation_config_dict)
            outputs = outputs[:, len(input_ids[0]):]  # Remove the prompt
        if self.device is not None:
            torch.cuda.empty_cache()

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def stream(
        self, prompt, stop_words: List[str], generation_config_dict: dict = None
    ) -> str:
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

        torch.manual_seed(generation_config_dict['seed'])

        generation_config_dict.pop("seed")

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )

        generation_config_dict = dict(
                input_ids=input_ids,
                do_sample=True,
                **generation_config_dict,
            )

        generation_config_dict["streamer"] = self.streamer
        thread = Thread(target=self.model.generate, kwargs=generation_config_dict)
        thread.start()
        for new_text in self.streamer:
            logger.info(f"Generated text: {new_text}")
            if new_text.strip() in stop_words:
                thread.join()
                break
            yield new_text
