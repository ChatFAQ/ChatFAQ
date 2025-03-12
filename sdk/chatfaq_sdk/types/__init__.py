from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


@dataclass
class KnowledgeItemImage:
    """
    An image contained in a KnowledgeItem.
    """

    image_name: str
    image_bytes: bytes
    knowledge_item: str = None
    image_caption: Optional[str] = None

    def dict(self):
        return {
            "knowledge_item": self.knowledge_item,
            "image_caption": self.image_caption,
        }

    def files(self):
        return {"image_file": (self.image_name, self.image_bytes)}


@dataclass
class KnowledgeItem:
    """
    A KnowledgeItem is a set of elements (titles, texts, urls, etc.) that are used for Retrieval Augmented Generation (RAG).
    """
    title: str
    content: str
    knowledge_base: Optional[str] = None
    data_source: Optional[str] = None
    section: Optional[str] = None
    url: Optional[str] = None
    page_number: Optional[int] = 0
    metadata: Optional[dict] = None
    images: Optional[List[KnowledgeItemImage]] = None
    id: Any = None
    created_date: Any = None
    updated_date: Any = None
    role: Any = None
    message: Any = None

    def dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "knowledge_base": self.knowledge_base,
            "data_source": self.data_source,
            "section": self.section,
            "url": self.url,
            "page_number": self.page_number,
            "metadata": self.metadata,
        }


@dataclass
class DataSource:
    kb_id: str
    ds_id: Optional[str]
    task_id: Optional[str]
    csv: Optional[str]
    pdf: Optional[str]
    url: Optional[str]


class WSType(Enum):
    rpc = "rpc"
    ai = "ai"
    parse = "parse"


@dataclass
class CacheConfig:
    """
    Configuration for caching LLM responses. For now it's only needed for Gemini.
    :param name: The name of the cache.
    :param ttl: The time to live for the cache in seconds.
    """
    name: str
    ttl: int = 3600  # Default TTL of 1 hour in seconds
