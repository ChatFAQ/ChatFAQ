from logging import getLogger

import ray
from django.db import transaction
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

logger = getLogger(__name__)


@ray.remote(num_cpus=0.2, resources={"tasks": 1})
def parse_url_task(ds_id, url):
    """
    Get the html from the url and parse it.
    Parameters
    ----------
    ds_id : int
        The primary key of the data source to which the crawled items will be added.
    url : str
        The url to crawl.
    """
    from back.apps.language_model.scraping.scraping.spiders.generic import (  # CI
        GenericSpider,
    )

    runner = CrawlerRunner(get_project_settings())
    runner.crawl(GenericSpider, start_urls=url, data_source_id=ds_id)


def parse_pdf(pdf_file, strategy, splitter, chunk_size, chunk_overlap):
    from io import BytesIO

    from chat_rag.data.parsers import parse_pdf as parse_pdf_method
    from chat_rag.data.splitters import get_splitter

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    logger.info(f"Splitter: {splitter}")
    logger.info(f"Strategy: {strategy}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"Chunk overlap: {chunk_overlap}")

    parsed_items = parse_pdf_method(
        file=pdf_file, strategy=strategy, split_function=splitter
    )

    return parsed_items


@ray.remote(num_cpus=1, resources={"tasks": 1})
def parse_pdf_task(ds_pk):
    """
    Parse a pdf file and return a list of KnowledgeItem objects.
    Parameters
    ----------
    ds_pk : int
        The primary key of the data source to parse.
    Returns
    -------
    k_items : list
        A list of KnowledgeItem objects.
    """
    from back.apps.language_model.models import DataSource, KnowledgeItem, KnowledgeItemImage

    logger.info("Parsing PDF file...")
    logger.info(f"PDF file pk: {ds_pk}")

   
    ds = DataSource.objects.get(pk=ds_pk)
    pdf_file = ds.original_pdf.read()
    strategy = ds.get_strategy().value
    splitter = ds.get_splitter().value
    chunk_size = ds.chunk_size
    chunk_overlap = ds.chunk_overlap

    parsed_items = parse_pdf(pdf_file, strategy, splitter, chunk_size, chunk_overlap)

    with transaction.atomic():
        for item in parsed_items:
            # Create and save the KnowledgeItem instance
            knowledge_item = KnowledgeItem(
                knowledge_base=ds.knowledge_base,
                data_source=ds,
                title=item.title,
                content=item.content,  # alnaf [[Image 0]] a;mda [[Image 2]]
                url=item.url,
                section=item.section,
                page_number=item.page_number,
                metadata=item.metadata,
            )
            knowledge_item.save()

            # For each image in the item, create and save a KnowledgeItemImage instance
            if item.images:
                for index, image in item.images.items():
                    image_instance = KnowledgeItemImage(
                        image_base64=image.image_base64,
                        knowledge_item=knowledge_item,
                        image_caption=image.image_caption,
                    )
                    image_instance.save()

                    # If the image does not have a caption, use a default caption
                    image_caption = (
                        image.image_caption if image.image_caption else f"Image {index}"
                    )

                    # Replace the placeholder image with the actual image markdown
                    knowledge_item.content = knowledge_item.content.replace(
                        f"[[Image {index}]]",
                        f"![{image_caption}]({image_instance.image_file.name})",
                    )
                    knowledge_item.save()
