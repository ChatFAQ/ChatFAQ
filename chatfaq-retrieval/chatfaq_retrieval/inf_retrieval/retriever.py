from typing import List, Tuple

import pandas as pd
from tqdm import tqdm
import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

class Retriever:
    """
    Class for retrieving the context for a given query using embeddings.
    """

    cached_tokenizers = {}
    cached_models = {}

    def __init__(self, df: pd.DataFrame = None,
                 context_col: str = 'answer',
                 model_name: str = 'intfloat/e5-small-v2',
                 use_cpu: bool = False,
                 ):
        """
        Parameters
        ----------
        df : pd.DataFrame
            Dataframe containing the context to be used for retrieval.
        model_name : str, optional
            Name of the model to be used for encoding the context, by default 'intfloat/multilingual-e5-base'
        context_col : str, optional
            Name of the column containing the context, by default 'answer'
        use_cpu : bool, optional
            Whether to use CPU for encoding, by default False
        """

        self.df = df
        self.device = 'cuda' if (not use_cpu and torch.cuda.is_available()) else 'cpu'

        print(f"Using device {self.device}")
        print(f"Loading model {model_name}")

        if model_name not in self.cached_tokenizers:
            self.cached_tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer = self.cached_tokenizers[model_name]

        if model_name == 'intfloat/e5-small-v2':
            self.tokenizer.model_max_length = 512 # Max length not defined on the tokenizer_config.json for the small model

        if model_name not in self.cached_models:
            self.cached_models[model_name] = AutoModel.from_pretrained(model_name,
                                                                       ).to(self.device)
        self.model = self.cached_models[model_name]

        self.context_col = context_col

        if self.df is not None:
            if 'embedding' in self.df.columns:
                self.embeddings = torch.tensor(self.df['embedding'].tolist(), dtype=torch.float32).to(self.device)
                print(f"Embeddings loaded from dataframe with shape {self.embeddings.shape}")



    def set_df(self, df: pd.DataFrame, batch_size: int = 1024, build_embeddings: bool = True, save_embeddings_path: str = None):
        """
        Sets the dataframe containing the context.
        Parameters
        ----------
        df : pd.DataFrame
            Dataframe containing the context to be used for retrieval.
        batch_size : int, optional
            Batch size to be used for encoding the context, by default 1024
        build_embeddings : bool, optional
            Whether to build the embeddings for the context, by default True
        save_embeddings_path : str, optional
            Path to save the embeddings to, by default None
        """
        # if exists self.embeddings clear them
        if hasattr(self, 'embeddings'):
            print("Clearing embeddings...")
            del self.embeddings

        self.df = df
        if build_embeddings:
            self.build_embeddings(batch_size=batch_size)
            if save_embeddings_path is not None:
                self.save_embeddings(save_embeddings_path)


    def build_embeddings(self, embedding_col: str = 'answer', batch_size: int = 1024):
        """
        Builds the embeddings for the context.
        Parameters
        ----------
        embedding_col : str, optional
            Name of the column to build the embeddings for and to be used for retrieval, by default 'answer'
        batch_size : int, optional
            Batch size to be used for encoding the context, by default 1024
        """
        print("Building embeddings...")
        answers = self.df[embedding_col].tolist()
        answers = ['passage: ' + answer for answer in answers] # add e5 prefix to answers
        self.embeddings = self.encode(answers, batch_size)

    def save_embeddings(self, path: str):
        """
        Saves the embeddings to a csv file.
        Parameters
        ----------
        path : str
            Path to the csv file.
        """
        print(f"Saving embeddings to {path}...")
        self.df['embedding'] = self.embeddings.cpu().tolist()
        self.df.to_parquet(path, index=False)

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

        # Tokenize sentences
        encoded_input = self.tokenizer(queries, padding=True, truncation=True, return_tensors='pt').to(self.device)

        all_embeddings = torch.tensor([])

        # Compute token embeddings
        with torch.inference_mode():
            for i in tqdm(range(0, len(encoded_input['input_ids']), batch_size), disable=disable_progess_bar):
                inputs = {key: val[i:i + batch_size] for key, val in encoded_input.items()}
                model_output = self.model(**inputs, return_dict=True)

                embeddings = self.average_pool(model_output.last_hidden_state, inputs['attention_mask'])

                del model_output

                embeddings = F.normalize(embeddings, p=2, dim=1).cpu()
                all_embeddings = torch.cat((all_embeddings, embeddings))

        torch.cuda.empty_cache()

        return all_embeddings

    def get_top_matches(self, query: str, top_k: int = 5, disable_progess_bar: bool = True) -> List[Tuple[str, float, int]]:
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

        Returns
        -------
        list
            List of tuples containing the context, the score and the index of the context.
        """

        assert hasattr(self, 'embeddings'), 'Embeddings not built. Call build_embeddings() first.'

        query = 'query: ' + query # Add e5 query prefix
        query_embedding = self.encode([query], disable_progess_bar=disable_progess_bar)
        scores = torch.mm(query_embedding, self.embeddings.transpose(0, 1))[0].cpu().tolist()  # Compute dot score between query and all document embeddings

        doc_score_triplets = list(
            zip(self.df.to_dict('records'), scores, range(len(self.df))))  # Combine docs, scores and an index

        doc_score_triplets = sorted(doc_score_triplets, key=lambda x: x[1], reverse=True)  # Sort by decreasing score

        if top_k == -1:  # Return all
            return doc_score_triplets

        return doc_score_triplets[:top_k]

    def get_top_matches_batch(self, queries: List[str], top_k: int = 5, disable_progess_bar: bool = False) -> List[List[Tuple[str, float, int]]]:
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

        Returns
        -------
        list
            List of tuples containing the context, the score and the index of the context.
        """

        assert hasattr(self, 'embeddings'), 'Embeddings not built. Call build_embeddings() first.'

        queries = ['query: ' + query for query in queries] # Add e5 query prefix

        queries_embeddings = self.encode(queries, disable_progess_bar=disable_progess_bar)
        scores = torch.mm(queries_embeddings, self.embeddings.transpose(0, 1)).cpu().tolist()

        doc_score_triplets = [
            list(zip(self.df.to_dict('records'), scores_per_query, range(len(self.df))))
            for scores_per_query in scores]

        doc_score_triplets = [
            sorted(doc_score_triplets_per_query, key=lambda x: x[1], reverse=True)
            for doc_score_triplets_per_query in doc_score_triplets]

        if top_k == -1:
            return doc_score_triplets

        return [doc_score_triplets_per_query[:top_k] for doc_score_triplets_per_query in doc_score_triplets]
    
    def get_contexts(self, matches):
        return [match[0][self.context_col] for match in matches]
