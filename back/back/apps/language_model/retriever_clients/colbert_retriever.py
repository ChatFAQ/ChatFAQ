from typing import List
import os
from logging import getLogger
import tempfile

from ragatouille import (
    RAGPretrainedModel as Retriever,
)  # Change name to avoid confusion

from django.core.files.storage import default_storage

from back.apps.language_model.models.data import KnowledgeItem
from back.apps.language_model.models.rag_pipeline import RAGConfig
from chat_rag.inf_retrieval.reference_checker import clean_relevant_references

from .utils import extract_images_urls


logger = getLogger(__name__)


class ColBERTRetriever:
    @classmethod
    def index(cls, rag_config: RAGConfig, k_items: List[KnowledgeItem]):
        # Generate a unique index path for this RAGConfig
        rag_config.generate_s3_index_path()
        s3_index_path = rag_config.s3_index_path
        index_root, index_name = s3_index_path.split("/")

        colbert_name = rag_config.retriever_config.model_name
        logger.info(
            f"Building index for knowledge base: {rag_config.knowledge_base.name} with colbert model: {colbert_name}"
        )

        contents = [item.content for item in k_items]
        contents_pk = [str(item.pk) for item in k_items]

        retriever = Retriever.from_pretrained(colbert_name, index_root=index_root)

        # Update the index path to use the unique index path
        local_index_path = retriever.index(
            index_name=index_name,
            collection=contents,
            document_ids=contents_pk,
            split_documents=False,
        )

        # Upload index files to S3
        for filename in os.listdir(local_index_path):
            local_file_path = os.path.join(local_index_path, filename)
            with open(local_file_path, "rb") as file:
                s3_file_path = os.path.join(s3_index_path, filename)
                default_storage.save(s3_file_path, file)
                os.remove(local_file_path)  # Delete local file after uploading to S3

        logger.info(
            f"Index built for knowledge base: {rag_config.knowledge_base.name} at {local_index_path}"
        )
        return local_index_path

    @classmethod
    def from_index(cls, rag_config: RAGConfig):
        if not rag_config.s3_index_path:
            raise ValueError("Index path not set for this RAGConfig.")

        instance = cls()

        index_root, index_name = rag_config.s3_index_path.split("/")
        index_root = f'{index_root}/colbert/indexes/'
        local_index_path = f'{index_root}/{index_name}'
        s3_index_folder = rag_config.s3_index_path

        os.makedirs(local_index_path, exist_ok=True)
        print(f"Downloading index files to {local_index_path} from S3 {rag_config.s3_index_path}")
        
        # Download index files from S3
        # listdir returns a tuple (dirs, files)
        for file_name in default_storage.listdir(s3_index_folder)[1]:  
            s3_file_path = os.path.join(s3_index_folder, file_name)
            local_file_path = os.path.join(local_index_path, file_name)
            with open(local_file_path, "wb") as local_file:
                local_file.write(default_storage.open(s3_file_path).read())

        # Load the index from the local directory
        logger.info(f"Loading index from {local_index_path}")
        instance.retriever = Retriever.from_index(index_path=local_index_path)

        # Test query for loading the searcher for the first time
        instance.retriever.search("test query", k=1, index_name=index_name)

        return instance

    def add_to_index(self, rag_config: RAGConfig, k_items: List[KnowledgeItem]):
        """Add knowledge items to the index of the given RAGConfig"""

        contents = [item.content for item in k_items]
        contents_pk = [str(item.pk) for item in k_items]

        index_name = rag_config.s3_index_path.split("/")[-1]

        self.retriever.add_to_index(
            new_document_ids=contents_pk,
            new_collection=contents,
            split_documents=False,
            index_name=index_name,
        )

        self._upload_updated_index_files(rag_config)

    def delete_from_index(self, rag_config: RAGConfig, k_item_ids: List[int]):
        """Delete knowledge items from the index of the given RAGConfig"""

        contents_pk = [str(id) for id in k_item_ids]

        index_name = rag_config.s3_index_path.split("/")[-1]

        self.retriever.delete_from_index(
            document_ids=contents_pk,
            index_name=index_name,
        )

        self._upload_updated_index_files(rag_config)

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
                result["score"] = (
                    result["score"] / 32.0
                )  # Normalize scores to be between 0 and 1

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

    def _upload_updated_index_files(
        self, rag_config: RAGConfig, index_path: str = None
    ):
        local_index_path = self._get_local_index_path() # return the local path of the index
        for filename in os.listdir(local_index_path):
            local_file_path = os.path.join(local_index_path, filename)
            with open(local_file_path, "rb") as file:
                s3_file_path = os.path.join(rag_config.s3_index_path, filename)
                default_storage.save(s3_file_path, file)

    def _get_local_index_path(self):
        return self.retriever.model.index_path
