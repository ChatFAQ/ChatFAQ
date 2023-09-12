import scrapy
from urllib.parse import urlparse

from back.apps.language_model.scraping.scraping.items import CustomItemLoader, GenericItem
from back.apps.language_model.tasks import llm_query_task


class GenericSpider(scrapy.Spider):
    name = "generic"
    allowed_domains = []
    start_urls = []

    def __init__(self, start_urls='', knowledge_base_id='', *a, **kw):
        self.knowledge_base_id = knowledge_base_id
        self.start_urls = start_urls.split(',')
        for url in self.start_urls:
            self.allowed_domains.append(urlparse(url).netloc)
            self.allowed_domains = list(set(self.allowed_domains))

        super().__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True})

    def parse(self, response):

        texts = response.xpath("//body//text()").getall()
        texts = [text.strip(" \n") for text in texts if text.strip(" \n") != '']
        for text in texts:
            item_loader = CustomItemLoader(item=GenericItem())
            item_loader.add_value("text", text)
            item_loader.add_value("url", response.url)
            yield item_loader.load_item()

        return
        for link in response.xpath("//a"):
            yield response.follow(link, callback=self.parse, meta={"playwright": True})

    def spider_closed(self, spider):
        llm_query_task.delay(recache_models=True)
