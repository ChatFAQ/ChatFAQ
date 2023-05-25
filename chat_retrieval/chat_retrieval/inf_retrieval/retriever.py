from typing import List, Tuple

import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class Retriever:
    """
    Class for retrieving the context for a given query.
    """

    def __init__(self, df: pd.DataFrame, model_name: str = 'sentence-transformers/all-mpnet-base-v2',
                 context_col: str = 'answer', use_cpu: bool = False):
        """
        Parameters
        ----------
        df : pd.DataFrame
            Dataframe containing the context to be used for retrieval.
        model_name : str, optional
            Name of the model to be used for encoding the context, by default 'sentence-transformers/all-mpnet-base-v2'
        context_col : str, optional
            Name of the column containing the context, by default 'answer'
        """
        self.df = df
        self.device = 'cuda' if (not use_cpu and torch.cuda.is_available()) else 'cpu'
        print(f"Using device {self.device}")
        print(f"Loading model {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name,
                                               # torch_dtype=torch.float16
                                               ).to(self.device)
        self.context_col = context_col

        if 'embedding' in self.df.columns:
            self.embeddings = torch.tensor(self.df['embedding'].tolist(), dtype=torch.float32).to(self.device)
            print(f"Embeddings loaded from dataframe with shape {self.embeddings.shape}")

    def build_embeddings(self, embedding_col: str = 'answer'):
        """
        Builds the embeddings for the context.
        Parameters
        ----------
        embedding_col : str, optional
            Name of the column to build the embeddings for and to be used for retrieval, by default 'answer'
        """
        print("Building embeddings...")
        answers = self.df[embedding_col].tolist()
        self.embeddings = self.encode(answers)

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

    def cls_pooling(self, model_output: torch.Tensor) -> torch.Tensor:
        """
        Returns the output of the first token.
        Parameters
        ----------
        model_output : torch.Tensor
            Output of the model.
        Returns
        -------
        torch.Tensor
            Output of the first token.
        """
        return model_output.last_hidden_state[:, 0]

    def mean_pooling(self, model_output: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Returns the mean of the embeddings.
        Parameters
        ----------
        model_output : torch.Tensor
            Output of the model.
        attention_mask : torch.Tensor
            Attention mask.
        Returns
        -------
        torch.Tensor
            Mean of the embeddings.
        """
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, texts: List[str]) -> torch.Tensor:
        """
        Returns the embeddings of the texts.
        Parameters
        ----------
        texts : List[str]
            List of texts to be encoded.
        Returns
        -------
        torch.Tensor
            Embeddings of the texts.
        """
        # Tokenize sentences
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)

        # Compute token embeddings
        with torch.inference_mode():
            model_output = self.model(**encoded_input, return_dict=True)

        # Perform pooling
        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        del model_output

        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings

    def get_context(self, query: str, top_k: int = 5) -> List[Tuple[str, float, int]]:
        """
        Returns the top_k most relevant context for the query.

        Parameters
        ----------
        query : str
            Query to be used for retrieval.
            top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.

        Returns
        -------
        list
            List of tuples containing the context, the score and the index of the context.
        """

        assert hasattr(self, 'embeddings'), 'Embeddings not built. Call build_embeddings() first.'

        query_embedding = self.encode([query])
        scores = torch.mm(query_embedding, self.embeddings.transpose(0, 1))[
            0].cpu().tolist()  # Compute dot score between query and all document embeddings
        doc_score_pairs = list(
            zip(self.df[self.context_col].tolist(), scores, range(len(self.df))))  # Combine docs, scores and an index
        doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)  # Sort by decreasing score

        if top_k == -1:  # Return all
            return doc_score_pairs
        return doc_score_pairs[:top_k]
