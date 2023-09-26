from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from back.apps.language_model.scraping.scraping.spiders.generic import GenericSpider


# ./manage.py scrape https://www.ca-moncommerce.com test

class Command(BaseCommand):
    help = "Scrape and creates a knowledge base from given url"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str)
        parser.add_argument("name", type=str)

    def handle(self, *args, **options):
        process = CrawlerProcess()

        process.crawl(GenericSpider, start_urls=options["url"], name=options["name"])
        process.start()  # the script will block here until the crawling is finished
