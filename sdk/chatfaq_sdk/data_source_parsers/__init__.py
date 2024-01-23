from typing import Iterator

from chatfaq_sdk.types import KnowledgeItem


class DataSourceParser:
    def __init__(self, data_source):
        self.data_source = data_source

    def parse(self, payload) -> Iterator[KnowledgeItem]:
        raise NotImplementedError()

    def __call__(self, payload) -> Iterator[KnowledgeItem]:
        return self.parse(payload)
