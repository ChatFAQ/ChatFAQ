from typing import Iterator

from chatfaq_sdk.types import KnowledgeItem


class DataSourceParser:
    def parse(self, data_source) -> Iterator[KnowledgeItem]:
        raise NotImplementedError()

    def __call__(self, kb_id, data_source) -> Iterator[KnowledgeItem]:
        for ki in self.parse(data_source):
            ki.knowledge_base = kb_id
            yield ki
