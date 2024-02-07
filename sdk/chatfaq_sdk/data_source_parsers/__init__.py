from typing import Iterator

from chatfaq_sdk.types import KnowledgeItem, DataSource


class DataSourceParser:
    def parse(self, data_source: DataSource) -> Iterator[KnowledgeItem]:
        raise NotImplementedError()

    def __call__(self, kb_id, ds_id, data_source: DataSource) -> Iterator[KnowledgeItem]:
        for ki in self.parse(data_source):
            ki.knowledge_base = kb_id
            ki.data_source = ds_id
            yield ki
