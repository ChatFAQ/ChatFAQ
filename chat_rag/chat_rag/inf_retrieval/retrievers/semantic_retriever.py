from typing import List, Tuple, Dict, Optional
from logging import getLogger

import numpy as np
import torch

from chat_rag.inf_retrieval.embedding_models.base_model import BaseModel

logger = getLogger(__name__)


class SemanticRetriever:
    """
    Class for retrieving the context for a given query using embeddings.
    """

    def __init__(
        self,
        data: Dict[str, List[str]] = None,
        embeddings: Optional[np.ndarray] = None,
        embedding_model: Optional[BaseModel] = None,
    ):
        """
        Parameters
        ----------
        data: Dict[str, List[str]], optional
            Dictionary containing the context to be used for retrieval, by default None
        embeddings: List[np.ndarray], optional
            List of embeddings to be used for retrieval, by default None
        embedding_model: BaseModel, optional
            Embedding model to be used for retrieval, by default None
        """

        # assert that the length of every column is the same
        if data is not None:
            assert (
                len(set([len(data[col]) for col in data])) == 1
            ), "All columns must have the same length"

        self.data = data
        self.len_data = len(data[list(data.keys())[0]]) if data is not None else None
        self.keys_list = list(data.keys()) if data is not None else None

        self.embeddings = (
            torch.from_numpy(embeddings) if embeddings is not None else None
        )

        if embeddings is None:
            logger.info(f"Embeddings not provided.")
        else:
            logger.info(f"Embeddings provided with shape {embeddings.shape}")

        self.embedding_model = embedding_model

    def get_top_matches(
        self,
        queries: List[str],
        top_k: int = 5,
        prefix: str = "query: ",
        threshold: float = None,
        disable_progress_bar: bool = False,
    ) -> List[Tuple[List[float], List[int]]]:
        """
        Returns the top_k most relevant context for the queries.

        Parameters
        ----------
        queries : List[str]
            Queries to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.
        disable_progress_bar : bool, optional
            Whether to disable the progress bar, by default True.
        prefix : str, optional
            Prefix or instruction to be added to the context, by default 'query: ' for e5 models.
        threshold : float, optional
            Minimum score to be returned, by default None.

        Returns
        -------
        list
            List containing tuples of scores and indexes of the context.
        """

        assert hasattr(
            self, "embeddings"
        ), "Embeddings not built. Call build_embeddings() first."

        queries = [prefix + query for query in queries]  # Add query prefix

        queries_embeddings = self.embedding_model.encode(
            queries, disable_progress_bar=disable_progress_bar
        )
        scores = (
            torch.mm(queries_embeddings, self.embeddings.transpose(0, 1)).cpu().numpy()
        )

        sorted_indices = np.argsort(scores, axis=1)[:, ::-1]

        # Use numpy's advanced indexing to get the sorted scores and indices
        sorted_scores = np.take_along_axis(scores, sorted_indices, axis=1)[
            :, :, None
        ]  # Add a new axis to be able to broadcast
        sorted_indexes = np.take_along_axis(
            np.broadcast_to(np.arange(scores.shape[1]), scores.shape),
            sorted_indices,
            axis=1,
        )[
            :, :, None
        ]  # Add a new axis to be able to broadcast

        # If threshold is given, create a mask for scores
        mask = (
            sorted_scores >= threshold
            if threshold is not None
            else np.ones_like(sorted_scores, dtype=bool)
        )

        # Use the mask to filter values
        sorted_scores = np.where(mask, sorted_scores, -np.inf).squeeze(-1)
        sorted_indexes = np.where(mask, sorted_indexes, -1).squeeze(-1)

        # remove the masked values
        sorted_scores = sorted_scores[sorted_scores != -np.inf].reshape(
            len(queries), -1
        )
        sorted_indexes = sorted_indexes[sorted_indexes != -1].reshape(len(queries), -1)

        # If top_k is not -1, truncate results
        if top_k != -1:
            sorted_scores = sorted_scores[:, :top_k]
            sorted_indexes = sorted_indexes[:, :top_k]

        scores_indexes = [
            (score_list, index_list)
            for score_list, index_list in zip(sorted_scores, sorted_indexes)
        ]
        return scores_indexes

    def _get_contexts(
        self, matches: Tuple[List[float], List[int]]
    ) -> List[Dict[str, str]]:
        """
        Returns the context for the matches.
        Parameters
        ----------
        matches : Tuple[List[float], List[int]]
            Tuple containing the scores and the index of the context.
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries containing the context.
        """
        # Resulting list of dictionaries
        context_list = []

        # Iterate through the matches
        for match in zip(*matches):
            context_dict = {}
            context_dict['similarity'] = match[0]
            # Extract data based on the keys and the matched index
            for key in self.keys_list:  # Using `self.keys_list` here
                context_dict[key] = self.data[key][match[1]]

            context_list.append(context_dict)

        return context_list

    def get_contexts(
        self, matches_batch: List[Tuple[List[float], List[int]]]
    ) -> List[List[Dict[str, str]]]:
        """
        Returns the context for the matches in a batch.
        Parameters
        ----------
        matches_batch : List[List[Tuple[float, int]]]
            List of lists of tuples containing the score and the index of the context.
        Returns
        -------
        List[List[Dict[str, str]]]
            List of lists of dictionaries containing the context.
        """
        return [self._get_contexts(matches) for matches in matches_batch]

    def retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        prefix: str = "query: ",
        threshold: float = None,
        disable_progress_bar: bool = False,
    ) -> List[List[Dict[str, str]]]:
        """
        Returns the context for the queries.
        Parameters
        ----------
        queries : List[str]
            List of queries to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5. If -1, all context are returned.
        disable_progress_bar : bool, optional
            Whether to disable the progress bar, by default True.
        prefix : str, optional
            Prefix or instruction to be added to the context, by default 'query: ' for e5 models.
        Returns
        -------
        List[List[Dict[str, str]]]
            List of lists of dictionaries containing the context.
        """

        matches_batch = self.get_top_matches(
            queries,
            top_k=top_k,
            disable_progress_bar=disable_progress_bar,
            prefix=prefix,
            threshold=threshold,
        )

        return self.get_contexts(matches_batch)
