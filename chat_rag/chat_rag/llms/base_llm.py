import os
from typing import Dict, List, Optional

from transformers import AutoConfig, AutoTokenizer


CONTEXT_PREFIX = {
    "en": "Information:",
    "fr": "Informations:",
    "es": "Información:",
}

NO_CONTEXT_SUFFIX = {
    "en": "No information provided.",
    "fr": "Aucune information n'a été fournie.",
    "es": "No se proporciona información.",
}


class LLM:
    def __init__(
        self,
        llm_name: str,
        model_max_length: int = None,
        trust_remote_code_tokenizer: bool = False,
        trust_remote_code_model: bool = False,
        **kwargs,
    ) -> None:
        auth_token = os.environ["HUGGINGFACE_KEY"]

        self.tokenizer = AutoTokenizer.from_pretrained(
            llm_name, trust_remote_code=trust_remote_code_tokenizer, token=auth_token
        )

        if model_max_length is not None:
            self.model_max_length = model_max_length
        else:
            self.config = AutoConfig.from_pretrained(
                llm_name, trust_remote_code=trust_remote_code_model, token=auth_token
            )
            self.model_max_length = (
                self.config.max_position_embeddings
                if self.config.max_position_embeddings is not None
                else self.tokenizer.model_max_length
            )

        self.has_chat_template = self.tokenizer.chat_template is not None
        print(f"Model max length: {self.model_max_length}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    async def astream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass

    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
    ) -> Optional[str | List[str]]:
        pass
