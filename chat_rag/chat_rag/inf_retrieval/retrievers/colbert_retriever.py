from typing import Optional, List, TypeVar, Union, Dict
from ragatouille import RAGPretrainedModel
from chat_rag.inf_retrieval.reference_checker import clean_relevant_references


class ColBERTRetriever:

    @classmethod
    def from_pretrained(cls,
                        model_name,  
                        n_gpu: int = -1,
        index_root: Optional[str] = None,
        ):
        instance = cls()
        instance.retriever = RAGPretrainedModel.from_pretrained(model_name, n_gpu=n_gpu, index_root=index_root)
        return instance
    
    @classmethod
    def from_index(cls,
                   index_path: str,
                   n_gpu: int = -1,
                   ):
        instance = cls()
        instance.retriever = RAGPretrainedModel.from_index(index_path, n_gpu=n_gpu)
        instance.use_plaid = False
        return instance
    
    def index(self, collection: List[str],  
              document_ids: Union[TypeVar("T"), List[TypeVar("T")]] = None,
        document_metadatas: Optional[list[dict]] = None,
        use_plaid: bool = False,
        bsize: int = 32,
        use_faiss: bool = True,
        max_document_length: int = 512,
        ):

        self.use_plaid = use_plaid

        if use_plaid:
            self.retriever.index(collection, document_ids, document_metadatas, split_documents=True, bsize=bsize, use_faiss=use_faiss, max_document_length=max_document_length)
        else:
            self.retriever.encode(collection, document_metadatas=document_metadatas, bsize=bsize, max_document_length=max_document_length)


    def _search_index(self, queries: List[str], top_k: int = 5):
        queries_results = self.retriever.search(
                queries,
                k=top_k,
            )

        query_maxlen = self.retriever.model.model_index.searcher.config.query_maxlen
        queries_results = [queries_results] if len(queries) == 1 else queries_results
        results = []
        for query_results, top_k in zip(queries_results, top_k):
            for result in query_results:
                result["similarity"] = result["score"] / query_maxlen

            # Filter out results not relevant to the query
            query_results = clean_relevant_references(query_results, score_key="similarity")

            results.append(query_results[:top_k])

        return results

    def retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        prefix: str = "",
        threshold: float = None,
        disable_progress_bar: bool = False,
    ) -> List[List[Dict[str, str]]]:

        if prefix:
            queries = [prefix + query for query in queries]
        
        if self.use_plaid:
            return self._search_index(queries, top_k)