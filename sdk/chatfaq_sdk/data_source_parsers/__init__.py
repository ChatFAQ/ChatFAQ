from typing import Iterator, List, Tuple

from chatfaq_sdk.types import KnowledgeItem, KnowledgeItemImage


class DataSourceParser:
    def parse(self, data_source) -> Iterator[Tuple[KnowledgeItem, List[KnowledgeItemImage]]]:
        raise NotImplementedError()

    def __call__(self, kb_id, data_source) -> Iterator[Tuple[KnowledgeItem, List[KnowledgeItemImage]]]:
        for ki in self.parse(data_source):
            ki.knowledge_base = kb_id
            yield ki
