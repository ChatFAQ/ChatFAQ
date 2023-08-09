import scrapy
from urllib.parse import urlparse


class GenericSpider(scrapy.Spider):
    name = "generic"
    allowed_domains = []
    start_urls = []

    def __init__(self, start_urls='', name='', *a, **kw):
        self.dataset_name = name
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
            yield {"text": text, "url": response.url}

        return
        for link in response.xpath("//a"):
            yield response.follow(link, callback=self.parse, meta={"playwright": True})
