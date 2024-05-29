from typing import Optional, List, TypeVar, Union, Dict
from ragatouille import RAGPretrainedModel
from chat_rag.inf_retrieval.reference_checker import clean_relevant_references
from ragatouille.data.preprocessors import llama_index_sentence_splitter



class ColBERTRetriever:

    @classmethod
    def from_pretrained(
        cls,
        model_name,
        n_gpu: int = -1,
        index_root: Optional[str] = None,
    ):
        """
        Loads the ColBERT retriever from a pretrained model WITHOUT an index.
        Parameters
        ----------
        model_name : str
            Name of the pretrained model.
        n_gpu : int, optional
            Number of GPUs to use. By default, value is -1, which means use all available GPUs or none if no GPU is available.
        index_root : Optional[str], optional
            The root directory where indexes will be stored. If None, will use the default directory, '.ragatouille/'.
        """
        instance = cls()
        instance.retriever = RAGPretrainedModel.from_pretrained(
            model_name, n_gpu=n_gpu, index_root=index_root
        )
        return instance

    @classmethod
    def from_index(
        cls,
        index_path: str,
        n_gpu: int = -1,
    ):
        """
        Loads the ColBERT retriever from an existing index.
        Parameters
        ----------
        index_path : str
            Path to the index.
        n_gpu : int, optional
            Number of GPUs to use. By default, value is -1, which means use all available GPUs or none if no GPU is available.
        """
        instance = cls()
        instance.retriever = RAGPretrainedModel.from_index(index_path, n_gpu=n_gpu)
        instance.use_plaid = False
        return instance

    def index(
        self,
        collection: List[str],
        document_ids: Union[TypeVar("T"), List[TypeVar("T")]] = None,
        document_metadatas: Optional[list[dict]] = None,
        use_plaid: bool = False,
        bsize: int = 32,
        use_faiss: bool = True,
        max_document_length: int = 512,
    ):
        """
        Index the documents for retrieval.
        Parameters
        ----------
        collection : List[str]
            List of documents to be indexed.
        document_ids : Union[TypeVar("T"), List[TypeVar("T")], optional
            List of document ids, by default None.
        document_metadatas : Optional[list[dict]], optional
            List of document metadatas, by default None.
        use_plaid : bool, optional
            Whether to use the PLAID index, by default False. Using PLAID is recommended for large collections, without it the documents are encoded in memory and the retrieval is slower.
        bsize : int, optional
            Batch size for encoding the documents, by default 32.
        use_faiss : bool, optional
            Whether to use FAISS for indexing, by default True.
        max_document_length : int, optional
            Maximum length of the document, by default 512.
        """

        self.use_plaid = use_plaid

        if use_plaid:
            self.retriever.index(
                collection,
                document_ids,
                document_metadatas,
                split_documents=True,
                bsize=bsize,
                use_faiss=use_faiss,
                max_document_length=max_document_length,
                overwrite_index='force_silent_overwrite',
            )
        else:
            self.retriever.encode(
                collection,
                document_metadatas=document_metadatas,
                bsize=bsize,
                max_document_length=max_document_length,
            )

    def _normalize_scores(self, queries_results, top_k, query_maxlen, threshold):
        """
        Normalize the scores of the retrieved documents by the query length and filter out irrelevant results.
        """
        results = []
        for query_results in queries_results:
            for result in query_results:
                result["similarity"] = result["score"] / query_maxlen

            # Filter out results not relevant to the query
            query_results = clean_relevant_references(
                query_results, score_key="similarity"
            )

            # Filter out results with similarity below threshold
            query_results = [
                result for result in query_results if result["similarity"] >= threshold
            ]
            results.append(query_results[:top_k])

        return results

    def _search_index(self, queries: List[str], top_k: int = 5, threshold: float = 0.0):
        """
        Search through the PLAID index. Useful for large collections.
        """
        queries_results = self.retriever.search(
            queries,
            k=top_k,
        )
        queries_results = [queries_results] if len(queries) == 1 else queries_results

        query_maxlen = self.retriever.model.model_index.searcher.config.query_maxlen

        results = self._normalize_scores(queries_results, top_k, query_maxlen, threshold)

        return results
    
    def _search_encodings(self, queries: List[str], top_k: int = 5, threshold: float = 0.0):
        """
        Search through the in memory encoded documents. Useful for small collections but not recommended for large collections.
        """
        queries_results = self.retriever.search_encoded_docs(
            queries,
            k=top_k,
        )
        queries_results = [queries_results] if len(queries) == 1 else queries_results

        query_maxlen = self.retriever.model.inference_ckpt.query_tokenizer.query_maxlen

        results = self._normalize_scores(queries_results, top_k, query_maxlen, threshold)

        return results

    def retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        prefix: str = "",
        threshold: float = 0.0,
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

        if prefix:
            queries = [prefix + query for query in queries]

        if self.use_plaid:
            return self._search_index(queries, top_k, threshold)
        else:
            return self._search_encodings(queries, top_k, threshold)
