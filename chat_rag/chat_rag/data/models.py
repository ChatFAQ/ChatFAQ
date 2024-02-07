from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Dict


class KnowledgeItemImage(BaseModel):
    """
    An image contained in a KnowledgeItem.
    """

    image_base64: str
    image_mime_type: str
    image_caption: Optional[str] = None


class KnowledgeItem(BaseModel):
    """
    A KnowledgeItem is a set of elements (titles, texts, urls, etc.) that are used for Retrieval Augmented Generation (RAG).
    """

    content: str
    title: Optional[str] = None
    section: Optional[str] = None
    url: Optional[str] = None
    page_number: Optional[int] = 0
    metadata: Optional[Dict] = None
    images: Optional[Dict[int, KnowledgeItemImage]] = Field(
        default_factory=dict
    )  # Dict of images with their index as key
