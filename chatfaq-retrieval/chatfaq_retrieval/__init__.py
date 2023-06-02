import time
from logging import getLogger

import pandas as pd
import torch

from chatfaq_retrieval.inf_retrieval.retriever import Retriever
from chatfaq_retrieval.prompt_generator.prompt_generator import PromptGenerator
from transformers import T5Tokenizer, T5ForConditionalGeneration

logger = getLogger(__name__)


# RetrieverAnswerer('../data/interim/chanel.csv', "google/flan-t5-base", "title", "text")

class RetrieverAnswerer:
    RETRIEVER_MODEL = 'sentence-transformers/multi-qa-MiniLM-L6-cos-v1'
    MAX_GPU_MEM = "18GiB"
    MAX_CPU_MEM = '12GiB'

    def __init__(self, base_data: str, model_name: str, context_col: str, embedding_col: str, use_cpu: bool = False):
        if not base_data.endswith(".csv"):
            raise "Only csv supported for base data file"
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

        # --- Set Up LLM ---
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)

        device_map = "auto" if (not self.use_cpu and torch.cuda.is_available()) else None # use gpu if available
        memory_device = {'cpu': self.MAX_CPU_MEM}
        dtype = torch.float32 # much faster for cpu, but consumes more memory
        if not self.use_cpu and torch.cuda.is_available():
            memory_device = {0: self.MAX_GPU_MEM}
            dtype = torch.bfloat16

        self.model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            device_map=device_map,
            torch_dtype=dtype,
            max_memory=memory_device
        )

        self._log_models_info()

    def query(self, text, seed=2):
        torch.manual_seed(seed)

        context = [value[0] for value in self.retriever.get_context(text, top_k=5)]
        prompt = self.prompt_gen.create_prompt(text, context, lang='en1', max_length=512)

        tokenizer_to = "cuda" if (not self.use_cpu and torch.cuda.is_available()) else 'cpu'

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(tokenizer_to)
        with torch.inference_mode():
            start_time = time.perf_counter()
            outputs = self.model.generate(
                input_ids,
                max_length=256,
                do_sample=True,
                top_k=50,
                top_p=0.95,
            )
            end_time = time.perf_counter()
            n_tokens = outputs.shape[1]
            logger.debug(f"Time per token: {(end_time - start_time) / n_tokens * 1000:.2f} ms")
        if tokenizer_to:
            torch.cuda.empty_cache()

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _log_models_info(self):
        logger.debug(f"Mem needed: {self.retriever.model.get_memory_footprint() / 1024 / 1024:.2f} MB")
        mb = self.retriever.embeddings.element_size() * self.retriever.embeddings.nelement() / 1024 / 1024
        logger.debug(f"Embeddings size: {mb} MB")

        # count number of parameters
        num = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        logger.debug(f'The model has {num / 1e9:.2f} billion trainable parameters')
        logger.debug(f"Mem needed: {self.model.get_memory_footprint() / 1024 / 1024 / 1024:.2f} GB")
