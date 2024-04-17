import scrapy
from urllib.parse import urlparse

from back.apps.language_model.scraping.scraping.items import CustomItemLoader, GenericItem
from back.apps.language_model.models.data import DataSource
from back.apps.language_model.ray_tasks import parse_html
import ray


class GenericSpider(scrapy.Spider):
    name = "generic"
    allowed_domains = []
    start_urls = []

    def __init__(self, start_urls='', data_source_id='', *a, **kw):
        self.data_source_id = data_source_id
        self.start_urls = start_urls.split(',')
        for url in self.start_urls:
            self.allowed_domains.append(urlparse(url).netloc.split(":")[0])
            self.allowed_domains = list(set(self.allowed_domains))

        ds = DataSource.objects.get(id=data_source_id)
        self.splitter = ds.splitter
        self.chunk_size = ds.chunk_size
        self.chunk_overlap = ds.chunk_overlap
        self.recursive = ds.recursive

        super().__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):
        # Not the most efficient way
        # TODO: try to launch multiple scrapy parse functions in parallel so that we can parse multiple pages at the same time
        k_items = ray.get(parse_html.remote(response.text, self.splitter, self.chunk_size, self.chunk_overlap))

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
