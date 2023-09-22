from typing import List, Tuple, Dict
from logging import getLogger

import numpy as np
import pandas as pd
from tqdm import tqdm
import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

logger = getLogger(__name__)

class Retriever:
    """
    Class for retrieving the context for a given query using embeddings.
    """

    cached_tokenizers = {}
    cached_models = {}

    def __init__(self, data: Dict[str, List[str]] = None,
                    embeddings: np.ndarray = None,
                    model_name: str = 'intfloat/e5-small-v2',
                    use_cpu: bool = False,
                ):
        """
        Parameters
        ----------
        data: Dict[str, List[str]], optional
            Dictionary containing the context to be used for retrieval, by default None
        embeddings: List[np.ndarray], optional
            List of embeddings to be used for retrieval, by default None
        model_name : str, optional
            Name of the model to be used for encoding the context, by default 'intfloat/multilingual-e5-base'
        use_cpu : bool, optional
            Whether to use CPU for encoding, by default False
        """

        # assert that the length of every column is the same
        if data is not None:
            assert len(set([len(data[col]) for col in data])) == 1, "All columns must have the same length"

        logger.debug(f"Use CPU: {use_cpu}, {torch.cuda.is_available()}")

        self.data = data
        self.len_data = len(data[list(data.keys())[0]]) if data is not None else None

        logger.debug(f"Data keys: {list(data.keys())}")
        logger.debug(f"Data length: {self.len_data}")
        # some examples of data:
        # print the first and last 5 elements of each column
        for col in data:
            logger.debug(f"First 5 elements of column {col}: {data[col][:5]}")
            logger.debug(f"Last 5 elements of column {col}: {data[col][-5:]}")

        self.embeddings = torch.from_numpy(embeddings) if embeddings is not None else None
        self.device = 'cuda' if (not use_cpu and torch.cuda.is_available()) else 'cpu'

        logger.debug(f"Using device {self.device}")
        logger.debug(f"Loading model {model_name}")

        if model_name not in self.cached_tokenizers:
            self.cached_tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer = self.cached_tokenizers[model_name]

        if model_name == 'intfloat/e5-small-v2':
            self.tokenizer.model_max_length = 512 # Max length not defined on the tokenizer_config.json for the small model

        if model_name not in self.cached_models:
            self.cached_models[model_name] = AutoModel.from_pretrained(model_name,
                                                                       ).to(self.device)
        self.model = self.cached_models[model_name]


    def build_embeddings(self, embedding_key: str = 'content', contents: List[str] = None, batch_size: int = 1, prefix: str = 'passage: '):
        """
        Builds the embeddings for the context.
        Parameters
        ----------
        embedding_key : str, optional
            Name of the column to build the embeddings for and to be used for retrieval, by default 'content'
        contents : List[str], optional
            List of contents to be encode, by default None
        batch_size : int, optional
            Batch size to be used for encoding the context, by default 1
        prefix : str, optional
            Prefix or instruction to be added to the context, by default 'passage: ' for e5 models.
        """
        print("Building embeddings...")
        if contents is None: # If contents is not provided, use the contents from the dataframe
            contents = self.data[embedding_key]
        contents = [prefix + content for content in contents] # add e5 prefix to answers
        print(len(contents))
        self.embeddings = self.encode(contents, batch_size)
        return self.embeddings

    def average_pool(self,
                     last_hidden_states: Tensor,
                    attention_mask: Tensor) -> Tensor:
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
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def encode(self, queries: List[str], batch_size: int = -1, disable_progess_bar: bool = False) -> torch.Tensor:
        """
        Returns the embeddings of the queries.
        Parameters
        ----------
        queries : List[str]
            List of queries to be encoded.
        batch_size : int, optional
            Batch size, by default -1 (no batching).
        disable_progess_bar : bool, optional
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
            for i in tqdm(range(0, len(queries), batch_size), disable=disable_progess_bar):

                # Tokenize sentences
                encoded_input = self.tokenizer(queries[i:i+batch_size], padding=True, truncation=True, return_tensors='pt').to(self.device)
                inputs = {key: val for key, val in encoded_input.items()}

                model_output = self.model(**inputs, return_dict=True)

                embeddings = self.average_pool(model_output.last_hidden_state, inputs['attention_mask'])

                del model_output

                embeddings = F.normalize(embeddings, p=2, dim=1).cpu()
                all_embeddings = torch.cat((all_embeddings, embeddings))

        torch.cuda.empty_cache()

        return all_embeddings

    def get_top_matches(self, query: str, top_k: int = 5, disable_progess_bar: bool = True, prefix: str = 'query: ') -> List[Tuple[float, int]]:
        """
        Returns the top_k most relevant context for the query.

        Parameters
        ----------
        query : str
            Query to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.
        disable_progess_bar : bool, optional
            Whether to disable the progress bar, by default True.
        prefix : str, optional
            Prefix or instruction to be added to the context, by default 'query: ' for e5 models.

        Returns
        -------
        list
            List of tuples containing the score and the index of the context.
        """

        assert hasattr(self, 'embeddings'), 'Embeddings not built. Call build_embeddings() first.'

        query = prefix + query # Add e5 query prefix
        query_embedding = self.encode([query], disable_progess_bar=disable_progess_bar)
        scores = torch.mm(query_embedding, self.embeddings.transpose(0, 1))[0].cpu().tolist()  # Compute dot score between query and all document embeddings

        scores_indexes = zip(scores, range(self.len_data))  # Combine the scores and an index

        scores_indexes = sorted(scores_indexes, key=lambda x: x[0], reverse=True)  # Sort by decreasing score

        if top_k == -1:  # Return all
            return scores_indexes

        # add the data to the scores_indexes according to the index
        return scores_indexes[:top_k]

    def get_top_matches_batch(self, queries: List[str], top_k: int = 5, disable_progess_bar: bool = False, prefix: str = 'query: ') -> List[List[Tuple[float, int]]]:
        """
        Returns the top_k most relevant context for the query.

        Parameters
        ----------
        queries : List[str]
            Queries to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.
        disable_progess_bar : bool, optional
            Whether to disable the progress bar, by default True.
        prefix : str, optional
            Prefix or instruction to be added to the context, by default 'query: ' for e5 models.

        Returns
        -------
        list
            List of tuples containing the score and the index of the context.
        """

        assert hasattr(self, 'embeddings'), 'Embeddings not built. Call build_embeddings() first.'

        queries = [prefix + query for query in queries] # Add e5 query prefix

        queries_embeddings = self.encode(queries, disable_progess_bar=disable_progess_bar)
        scores = torch.mm(queries_embeddings, self.embeddings.transpose(0, 1)).cpu().tolist()

        scores_indexes = [
            zip(scores_per_query, range(self.len_data))
            for scores_per_query in scores]

        scores_indexes = [
            sorted(scores_indexes_per_query, key=lambda x: x[0], reverse=True)
            for scores_indexes_per_query in scores_indexes]

        if top_k == -1:
            return scores_indexes

        return [score_indexes_per_query[:top_k] for score_indexes_per_query in scores_indexes]
    

    def get_contexts(self, matches: List[Tuple[float, int]]) -> List[Dict[str, str]]:
        keys = list(self.data.keys())
        return [{keys[i]: self.data[keys[i]][match[1]] for i in range(len(keys))} for match in matches]

    def get_contexts_batch(self, matches_batch: List[List[Tuple[float, int]]]) -> List[List[Dict[str, str]]]:
        keys = list(self.data.keys())
        return [[{keys[i]: self.data[keys[i]][match[1]] for i in range(len(keys))} for match in matches] for matches in matches_batch]
        
