from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum


@dataclass
class KnowledgeItem:
    """
    A KnowledgeItem is a set of elements (titles, texts, urls, etc.) that are used for Retrieval Augmented Generation (RAG).
    """
    title: str
    content: str
    knowledge_base: Optional[str] = None
    section: Optional[str] = None
    url: Optional[str] = None
    page_number: Optional[int] = 0
    metadata: Optional[dict] = None

    dict = asdict


@dataclass
class Image:
    """
    An image contained in a KnowledgeItem.
    """
    file_name: str
    content: bytes

    dict = asdict


@dataclass
class KnowledgeItemImage:
    """
    An image contained in a KnowledgeItem.
    """

    image_file: Image
    knowledge_item: str
    image_caption: Optional[str] = None

    def dict(self):
        return {
            "image_file": (self.image_file.file_name, self.image_file.content),
            "knowledge_item": self.knowledge_item,
            "image_caption": self.image_caption,
        }


class WSType(Enum):
    rpc = "rpc"
    llm = "llm"
    parse = "parse"
