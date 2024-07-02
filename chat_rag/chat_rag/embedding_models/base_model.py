from logging import getLogger
from typing import List

import torch
import torch.nn.functional as F
from torch import Tensor
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

logger = getLogger(__name__)


class BaseModel:
    """
    Class for generating embeddings for a given text.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
        use_cpu: bool = False,
        huggingface_key: str = None,
        trust_remote_code: bool = False,
        **kwargs,
    ):
        """
        Parameters
        ----------
        model_name : str, optional
            Name of the model to be used for encoding the context, by default 'intfloat/multilingual-e5-base'
        use_cpu : bool, optional
            Whether to use CPU for encoding, by default False
        huggingface_key : str, optional
            Huggingface key to be used for private models, by default None
        trust_remote_code : bool, optional
            Whether to trust the remote code, by default False
        """

        self.device = "cuda" if (not use_cpu and torch.cuda.is_available()) else "cpu"

        logger.info(f"Using device {self.device}")
        logger.info(f"Loading model {model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=huggingface_key
        )

        self.model = AutoModel.from_pretrained(
            model_name,
            token=huggingface_key,
            trust_remote_code=trust_remote_code,
            **kwargs,
        ).to(self.device)

    def average_pool(
        self, last_hidden_states: Tensor, attention_mask: Tensor
    ) -> Tensor:
        """
        Average pooling strategy.
        Parameters
        ----------
        last_hidden_states : Tensor
            Last hidden states of the model.
        attention_mask : Tensor
            Attention mask of the model.
        Returns
        -------
        Tensor
            Embeddings of the queries.
        """
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def encode(
        self,
        queries: List[str],
        batch_size: int = -1,
        disable_progress_bar: bool = False,
    ) -> torch.Tensor:
        """
        Returns the embeddings of the queries.
        Parameters
        ----------
        queries : List[str]
            List of queries to be encoded.
        batch_size : int, optional
            Batch size, by default -1 (no batching).
        disable_progress_bar : bool, optional
            Whether to disable the progress bar, by default False.
        Returns
        -------
        torch.Tensor
            Embeddings of the queries.
        """
        if batch_size == -1:
            batch_size = len(queries)

        all_embeddings = torch.tensor([])

        # Compute token embeddings
        with torch.inference_mode():
            for i in tqdm(
                range(0, len(queries), batch_size), disable=disable_progress_bar
            ):
                # Tokenize sentences
                encoded_input = self.tokenizer(
                    queries[i : i + batch_size],
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                ).to(self.device)
                inputs = {key: val for key, val in encoded_input.items()}

                model_output = self.model(**inputs, return_dict=True)

                embeddings = self.average_pool(
                    model_output.last_hidden_state, inputs["attention_mask"]
                )

                del model_output

                embeddings = F.normalize(embeddings, p=2, dim=1).cpu()
                all_embeddings = torch.cat((all_embeddings, embeddings))

        torch.cuda.empty_cache()

        return all_embeddings

    def build_embeddings(
        self,
        contents: List[str] = None,
        batch_size: int = 1,
        prefix: str = "",
        disable_progress_bar: bool = False,
    ):
        """
        Builds the embeddings for the context.
        Parameters
        ----------
        contents : List[str], optional
            List of contents to be encode, by default None
        batch_size : int, optional
            Batch size to be used for encoding the context, by default 1
        prefix : str, optional
            Prefix or instruction to be added to the context. Sometimes is used for instruct embedding models like Instructor models or intfloat/multilingual-e5-large-instruct.
        """
        logger.info("Building embeddings...")

        contents = [prefix + content for content in contents]  # add prefix to answers
        embeddings = self.encode(contents, batch_size, disable_progress_bar)

        return embeddings
