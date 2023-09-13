from dataclasses import dataclass

@dataclass
class KnowledgeItem:
    """
    A KnowledgeItem is a set of elements (titles, texts, urls, etc.) that are use for Retrieval Augmented Generation (RAG).  
    """
    content: str
    title: str = ""
    section: str = ""
    url: str = ""
    page_number: int = 0