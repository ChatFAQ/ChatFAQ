from typing import List

from ragatouille import RAGPretrainedModel

from back.apps.language_model.models.data import KnowledgeItem
from back.apps.language_model.models.rag_pipeline import RAGConfig

from .utils import extract_images_urls


class ColBERTRetriever:
    
    @classmethod
    def create_index(cls, rag_config: RAGConfig, colbert_name: str = "colbert-ir/colbertv2.0"):
        """Creates the index for the given RAGConfig"""
        items = KnowledgeItem.objects.filter(knowledge_base=rag_config.knowledge_base)
        
        contents = [item.content for item in items]
        contents_pk = [item.pk for item in items]

        RAG = RAGPretrainedModel.from_pretrained(colbert_name)

        index_name = f"{rag_config.name}_index"

        index_path = RAG.index(
            index_name=index_name,
            collection=contents,
            document_ids=contents_pk,
            split_documents=False,
        )

