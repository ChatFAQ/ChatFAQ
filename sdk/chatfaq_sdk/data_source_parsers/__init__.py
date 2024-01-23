from typing import Iterator

from chatfaq_sdk.types import KnowledgeItem


class DataSourceParser:
    def parse(self, payload) -> Iterator[KnowledgeItem]:
        raise NotImplementedError()

    def __call__(self, payload) -> Iterator[KnowledgeItem]:
        return self.parse(payload)
