import csv
from typing import Iterator
from chatfaq_sdk import DataSourceParser
from chatfaq_sdk.types import KnowledgeItem
from examples import make_chatfaq_sdk
from examples.model_example.fsm_definition import fsm_definition


class CustomDataSourceParser(DataSourceParser):
    # it reads the raw binary 'file' as a csv file
    def parse(self, data_source):
        yield KnowledgeItem(
            title="title1",
            content="content1",
            url="http://www.exaple.com/1"
        )
        yield KnowledgeItem(
            title="title2",
            content="content2",
            url="http://www.exaple.com/2"
        )
        yield KnowledgeItem(
            title="title3",
            content="content3",
            url="http://www.exaple.com/3"
        )


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="model_fsm",
        fsm_definition=fsm_definition,
        data_source_parsers={"three_static_kis": CustomDataSourceParser()}
    )
    sdk.connect()
