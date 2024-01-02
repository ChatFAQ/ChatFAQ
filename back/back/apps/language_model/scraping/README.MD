# Generic Scrapy scraper

This is a generic scraper that can be used to scrape any website and generate knowledge items from it.

It runs as a celery task automatically

If you want to run it froma  terminal:

    scrapy crawl generic -a knowledge_base_id=<KNOWLEDGE_BASE_ID> -a start_urls=<START_URL_1,START_URL_2,START_URL_3,...>
