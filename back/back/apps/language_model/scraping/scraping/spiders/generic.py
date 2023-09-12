import scrapy
from urllib.parse import urlparse

from back.apps.language_model.scraping.scraping.items import CustomItemLoader, GenericItem
from back.apps.language_model.models import Dataset
from back.apps.language_model.tasks import llm_query_task
from chatfaq_retrieval.data.parsers import parse_html
from chatfaq_retrieval.data.splitters import get_splitter



class GenericSpider(scrapy.Spider):
    name = "generic"
    allowed_domains = []
    start_urls = []

    def __init__(self, start_urls='', dataset_id='', *a, **kw):
        self.dataset_id = dataset_id
        self.start_urls = start_urls.split(',')
        for url in self.start_urls:
            self.allowed_domains.append(urlparse(url).netloc)
            self.allowed_domains = list(set(self.allowed_domains))

        ds = Dataset.objects.get(id=dataset_id)
        self.splitter = get_splitter(ds.splitter, ds.chunk_size, ds.chunk_overlap)
        self.recursive = ds.recursive

        super().__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        k_items = parse_html(text=response.text, split_function=self.splitter)

        for k_item in k_items:
            item_loader = CustomItemLoader(item=GenericItem())
            item_loader.add_value("content", k_item.content)
            item_loader.add_value("title", k_item.title)
            # item_loader.add_value("section", k_item.section) Current parser does not extract the section
            item_loader.add_value("url", response.url)
            item_loader.add_value("page_number", k_item.page_number)
            yield item_loader.load_item()

        if self.recursive:
            for link in response.xpath("//a"):
                yield response.follow(link, callback=self.parse, meta={"playwright": True})

    def spider_closed(self, spider):
        llm_query_task.delay(None, None, None, None, None, True)
