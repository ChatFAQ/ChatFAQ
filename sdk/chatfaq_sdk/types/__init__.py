from typing import Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class KnowledgeItem:
    """
    A KnowledgeItem is a set of elements (titles, texts, urls, etc.) that are used for Retrieval Augmented Generation (RAG).
    """
    content: str
    title: Optional[str] = None
    section: Optional[str] = None
    url: Optional[str] = None
    page_number: Optional[int] = 0
    metadata: Optional[dict] = None


class WSType(Enum):
    rpc = "rpc"
    llm = "llm"
    parse = "parse"
