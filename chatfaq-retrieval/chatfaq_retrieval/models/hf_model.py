from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, T5Tokenizer, T5ForConditionalGeneration


class HFModel:

    MAX_GPU_MEM = "18GiB" # Why this
    MAX_CPU_MEM = '12GiB'

    def __init__(self, repo_id: str, use_cpu: bool, tokenizer_kwargs: dict = None, model_kwargs: dict = None):
        """
        Initializes the model and tokenizer.
        Parameters
        ----------
        repo_id : str
            The huggingface repo id.
        use_cpu : bool
            Whether to use cpu or gpu.
        tokenizer_kwargs : dict
            Keyword arguments for the tokenizer.
        model_kwargs : dict
            Keyword arguments for the model.
        """


        ######### JUST FOR TESTING #########
        if 't5' in repo_id: 
            self.tokenizer, self.model = self.get_t5(repo_id)


        device_map = "auto" if (not use_cpu and torch.cuda.is_available()) else None # use gpu if available
        self.device = "cuda:0" if (not use_cpu and torch.cuda.is_available()) else None  # For moving tensors to the GPU
        memory_device = {'cpu': self.MAX_CPU_MEM}
        if not use_cpu and torch.cuda.is_available():
            memory_device = {0: self.MAX_GPU_MEM} 

        self.tokenizer = AutoTokenizer.from_pretrained(repo_id, **tokenizer_kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(
            repo_id, 
            device_map=device_map,
            torch_dtype="auto",
            max_memory=memory_device,
            low_cpu_mem_usage=True,
            **model_kwargs,
        )
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True)

    def get_t5(self, repo_id):
        ######### JUST FOR TESTING #########
        tokenizer = T5Tokenizer.from_pretrained(repo_id)

        device_map = "auto" if (not self.use_cpu and torch.cuda.is_available()) else None # use gpu if available
        memory_device = {'cpu': self.MAX_CPU_MEM}
        dtype = torch.float32 # much faster for cpu, but consumes more memory
        if not self.use_cpu and torch.cuda.is_available():
            memory_device = {0: self.MAX_GPU_MEM}
            dtype = torch.bfloat16

        return tokenizer, T5ForConditionalGeneration.from_pretrained(
                repo_id,
                device_map=device_map,
                torch_dtype=dtype,
                max_memory=memory_device
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
        torch.manual_seed(seed)

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        generation_kwargs = dict(
            input_ids=input_ids,
            do_sample=True,
            **generation_kwargs,
        )
        if streaming:
            generation_kwargs['streamer'] = self.streamer
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            for new_text in self.streamer:
                yield new_text
        else:
            with torch.inference_mode():
                outputs = self.model.generate(**generation_kwargs)
            if self.device is not None:
                torch.cuda.empty_cache()

            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


