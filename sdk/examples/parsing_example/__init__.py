import csv
from typing import Iterator
from chatfaq_sdk import DataSourceParser
from chatfaq_sdk.types import KnowledgeItem, KnowledgeItemImage
from examples import make_chatfaq_sdk
from examples.model_example.fsm_definition import fsm_definition


class CustomDataSourceParser(DataSourceParser):
    # it reads the raw binary 'file' as a csv file
    def parse(self, data_source):
        image = open("./example_images/logo.png", "rb")
        image_bytes = image.read()
        image_name = image.name.split("/")[-1]
        yield KnowledgeItem(
            title="title1",
            content="begin content 1 [[Image 0]] end content 1",
            url="http://www.exaple.com/1",
            images=[KnowledgeItemImage(
                image_name=image_name,
                image_bytes=image_bytes,
                image_caption="image1",
            )]
        )
        yield KnowledgeItem(
            title="title2",
            content="begin content 2 [[Image 0]] end content 2",
            url="http://www.exaple.com/2",
            images=[KnowledgeItemImage(
                image_name=image_name,
                image_bytes=image_bytes,
                image_caption="image2",
            )]
        )
        yield KnowledgeItem(
            title="title3",
            content="begin content 3 [[Image 0]] end content 3",
            url="http://www.exaple.com/3",
            images=[KnowledgeItemImage(
                image_name=image_name,
                image_bytes=image_bytes,
                image_caption="image3",
            )]
        )


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="model_fsm",
        fsm_definition=fsm_definition,
        data_source_parsers={"three_static_kis": CustomDataSourceParser()}
    )
    sdk.connect()
