import os
from collections.abc import Sequence
from logging import getLogger
from threading import Thread
from typing import Dict, List

import regex
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

from chat_rag.llms import LLM

logger = getLogger(__name__)

# TODO: Refactor this class


class StopPatternCriteria(StoppingCriteria):
    """
    Stopping criteria that checks if the text generation contains a stop pattern.
    Inspired by https://github.com/microsoft/guidance/blob/e3c6fe93fa00cb86efc130bbce22aa29100936d4/guidance/llms/_transformers.py#L567
    """

    def __init__(self, stop_pattern, tokenizer, prefix_length):
        if isinstance(stop_pattern, str):
            self.stop_patterns = [regex.compile(stop_pattern)]
        else:
            self.stop_patterns = [
                regex.compile(pattern.strip()) for pattern in stop_pattern
            ]
        self.tokenizer = tokenizer
        self.prefix_length = prefix_length

    def __call__(self, input_ids, scores):
        # handle 1D inputs
        if not isinstance(input_ids[0], Sequence) and not (
            hasattr(input_ids[0], "shape") and len(input_ids[0].shape) > 0
        ):
            input_ids = [input_ids]

        text_generations = self.tokenizer.batch_decode(input_ids)

        # check if all text generations have a stop pattern, so we can stop the batch inference
        all_done = True
        for text_generation in text_generations:
            found = False
            for stop_pattern in self.stop_patterns:
                if stop_pattern.search(text_generation[self.prefix_length :].strip()):
                    found = True
            if not found:
                all_done = False
                break

        return all_done


class HFModel(LLM):
    MAX_GPU_MEM = "18GiB"  # Why this
    MAX_CPU_MEM = "12GiB"

    def __init__(
        self,
        llm_name: str,
        use_cpu: bool,
        load_in_8bit: bool = False,
        use_fast_tokenizer: bool = True,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        revision: str = "main",
        **kwargs,
    ):
        """
        Initializes the model and tokenizer.
        Parameters
        ----------
        llm_name : str
            The huggingface repo id.
        use_cpu : bool
            Whether to use cpu or gpu.
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
        """
        super().__init__(
            llm_name,
            trust_remote_code_tokenizer=trust_remote_code_tokenizer,
            trust_remote_code_model=trust_remote_code_model,
            **kwargs,
        )
        self.use_cpu = use_cpu
        auth_token = os.environ["HUGGINGFACE_KEY"]

        device_map = (
            "auto" if (not use_cpu and torch.cuda.is_available()) else None
        )  # use gpu if available
        self.device = (
            "cuda:0" if (not use_cpu and torch.cuda.is_available()) else None
        )  # For moving tensors to the GPU
        memory_device = {"cpu": self.MAX_CPU_MEM}
        if not use_cpu and torch.cuda.is_available():
            memory_device = {0: self.MAX_GPU_MEM}

        logger.info(f"Loading HF model from {llm_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            llm_name,
            token=auth_token,
            use_fast=use_fast_tokenizer,
            revision=revision,
            trust_remote_code=trust_remote_code_tokenizer,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            device_map=device_map,
            torch_dtype="auto",
            max_memory=memory_device,
            low_cpu_mem_usage=True,
            token=auth_token,
            revision=revision,
            load_in_8bit=load_in_8bit,
            trust_remote_code=trust_remote_code_model,
        )
        self.streamer = TextIteratorStreamer(
            self.tokenizer, skip_special_tokens=True, skip_prompt=True
        )

    def generate(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. List of pairs (role, content).
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
        torch.manual_seed(generation_config_dict["seed"])

        generation_config_dict.pop("seed")

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )

        if stop_words is not None:
            stopping_criteria = StopPatternCriteria(
                stop_words, self.tokenizer, len(prompt)
            )
            generation_config_dict["stopping_criteria"] = StoppingCriteriaList(
                [stopping_criteria]
            )

        generation_config_dict = dict(
            input_ids=input_ids,
            do_sample=True,
            **generation_config_dict,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        generation_config_dict.pop("name")

        with torch.inference_mode():
            outputs = self.model.generate(**generation_config_dict)
            outputs = outputs[:, len(input_ids[0]) :]  # Remove the prompt
        if self.device is not None:
            torch.cuda.empty_cache()

        output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # remove all stop words from output TODO: This is a hack, we should improve the stopping criteria, but it's not easy when one stop word is longer than one token
        if stop_words is not None:
            for stop_word in stop_words:
                output = output.replace(stop_word.strip(), "")

        return output

    def stream(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict = None,
        lang: str = "en",
        stop_words: List[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text from a prompt using the model in streaming mode.
        Parameters
        ----------
        messages : List[Tuple[str, str]]
            The messages to use for the prompt. List of pairs (role, content).
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

        torch.manual_seed(generation_config_dict["seed"])

        generation_config_dict.pop("seed")

        prompt = self.format_prompt(messages, contexts, **prompt_structure_dict, lang=lang)

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )

        generation_config_dict = dict(
            input_ids=input_ids,
            do_sample=True,
            **generation_config_dict,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        generation_config_dict.pop("name")

        generation_config_dict["streamer"] = self.streamer
        thread = Thread(target=self.model.generate, kwargs=generation_config_dict)
        thread.start()
        for new_text in self.streamer:
            if (
                new_text in stop_words
            ):  # TODO: This is a hack, we should use the stopping criteria, but it's not easy when one stop word is longer than one token
                thread.join()
                break
            yield new_text
