from typing import Any, Dict, List

import bm25s


class BM25Retriever:
    def __init__(self, corpus: List[Dict[str, Any]], stemmer=None):
        """
        Retrieve documents from a corpus using BM25.
        Parameters
        ----------
        corpus : List[Dict[str, Any]]
            List of dictionaries with the keys "content" and "title".
        stemmer : str, optional
            Stemmer to use, by default None.
        """
        self.stemmer = stemmer
        self.retriever = bm25s.BM25(corpus=corpus)
        self.index(corpus=corpus)

    def index(self, corpus):
        assert all(
            "content" in doc for doc in corpus
        ), "All documents in the corpus must have a 'content' key."

        texts = [doc["content"] for doc in corpus]
        corpus_tokens = bm25s.tokenize(texts, stemmer=self.stemmer, show_progress=False)
        self.retriever.index(corpus_tokens, show_progress=False)

    def retrieve(
        self,
        queries: List[str],
        top_k: int = 3,
        disable_progress_bar: bool = False,
        **kwargs,
    ) -> List[List[Dict[str, Any]]]:
        queries_tokens = bm25s.tokenize(queries, stemmer=self.stemmer)
        results, scores = self.retriever.retrieve(
            queries_tokens, k=top_k, show_progress=not disable_progress_bar
        )
        results = results.tolist()

        # Add scores to the results
        results_with_score = []
        for results_query, scores_queries in zip(results, scores):
            results_with_score.append(
                [
                    {
                        **doc,
                        "score": score.item(), # from np.float32 to float
                    }
                    for doc, score in zip(results_query, scores_queries)
                ]
            )

        return results_with_score
