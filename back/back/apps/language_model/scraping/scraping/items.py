# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Compose, Join, TakeFirst, Identity

from back.apps.language_model.scraping.scraping.processors import rm_dupl_ws, split


class CustomItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = Compose(TakeFirst(), rm_dupl_ws)

    join_def_proc = {
        "input_processor": default_input_processor,
        "output_processor": Compose(Join(), rm_dupl_ws, str.strip)
    }

    split_def_proc = lambda char: {
        "input_processor": CustomItemLoader.default_input_processor,
        "output_processor": Compose(TakeFirst(), rm_dupl_ws, split(char))
    }


class GenericItem(scrapy.Item):
    text = scrapy.Field()
    url = scrapy.Field()
