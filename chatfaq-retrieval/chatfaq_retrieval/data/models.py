from dataclasses import dataclass

@dataclass
class Context:
    """
    A context is a list of elements (titles, texts, urls, etc.) that are use for Retrieval Augmented Generation (RAG).
    """
    content: str
    title: str = ""
    url: str = ""
    category: str = ""
    page_number: int = 0