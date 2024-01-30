from typing import List
import os
from logging import getLogger

from ragatouille import (
    RAGPretrainedModel as Retriever,
)  # Change name to avoid confusion

from back.apps.language_model.models.data import KnowledgeItem
from back.apps.language_model.models.rag_pipeline import RAGConfig
from chat_rag.inf_retrieval.reference_checker import clean_relevant_references

from .utils import extract_images_urls


logger = getLogger(__name__)

class ColBERTRetriever:
    @classmethod
    def index(cls, rag_config: RAGConfig, k_items: List[KnowledgeItem]):
        """Creates the index for the given RAGConfig"""

        colbert_name = rag_config.retriever_config.model_name

        logger.info(f"Building index for knowledge base: {rag_config.knowledge_base.name} with colbert model: {colbert_name}")

        contents = [item.content for item in k_items]
        contents_pk = [str(item.pk) for item in k_items]

        retriever = Retriever.from_pretrained(colbert_name, index_root="indexes/")

        index_path = retriever.index(
            index_name=f"{rag_config.name}_index",
            collection=contents,
            document_ids=contents_pk,
            split_documents=False,
        )

        logger.info(f"Index built for knowledge base: {rag_config.knowledge_base.name} at {index_path}")

        return index_path

    @classmethod
    def from_index(cls, rag_config: RAGConfig):
        """Load an Index and the associated ColBERT encoder from an existing RAG index"""

        instance = cls()

        index_path = os.path.join(
            "indexes", "colbert", "indexes", f"{rag_config.name}_index"
        )
        instance.retriever = Retriever.from_index(index_path=index_path)

        # Test query for loading the searcher for the first time
        instance.retriever.search("test query")

        return instance
    
    def add_to_index(self, rag_config: RAGConfig, k_items: List[KnowledgeItem]):
        """Add knowledge items to the index of the given RAGConfig"""

        contents = [item.content for item in k_items]
        contents_pk = [str(item.pk) for item in k_items]

        self.retriever.add_to_index(
            new_document_ids=contents_pk,
            new_collection=contents,
            split_documents=False,
            index_name=f"{rag_config.name}_index",
        )

    def delete_from_index(self, rag_config: RAGConfig, k_item_ids: List[int]):
        """Delete knowledge items from the index of the given RAGConfig"""
        
        contents_pk = [str(id) for id in k_item_ids]

        self.retriever.delete_from_index(
            document_ids=contents_pk,
         #   index_name=f"{rag_config.name}_index",
        )

    def retrieve(self, queries: List[str], top_k: int = 5):
        """
        Returns the context for the queries.
        Parameters
        ----------
        queries : List[str]
            List of queries to be used for retrieval.
        top_k : int, optional
            Number of context to be returned, by default 5.
        """

        queries_results = self.retriever.search(queries, k=top_k)

        # If only one query was passed, the result is not a list
        queries_results = [queries_results] if len(queries) == 1 else queries_results

        results = []
        for query_results in queries_results:
            for result in query_results:
                result["score"] = result["score"] / 32.0 # Normalize scores to be between 0 and 1
                

            # Filter out results not relevant to the query
            query_results = clean_relevant_references(query_results)

            ids = [int(result["document_id"]) for result in query_results]

            items = KnowledgeItem.objects.filter(pk__in=ids)

            query_results = [
                {
                    "knowledge_item_id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "url": item.url,
                    "section": item.section,
                    "role": item.role,
                    "page_number": str(item.page_number) if item.page_number else None,
                    "similarity": query_results[ndx]["score"],
                    "image_urls": extract_images_urls(item.content)
                    if item.content
                    else {},
                }
                for ndx, item in enumerate(items)
            ]

            results.append(query_results)

        return results
