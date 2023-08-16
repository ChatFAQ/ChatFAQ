# -*- coding: utf-8 -*-
from back.apps.language_model.models import Dataset, Item
from asgiref.sync import sync_to_async

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class GenericPipeline(object):
    ds = None

    async def process_item(self, item, spider):
        if not self.ds:
            self.ds = await sync_to_async(Dataset.objects.get)(id=spider.dataset_id)

        _item = await sync_to_async(Item.objects.create)(
            dataset=self.ds,
            answer=item['text'],
            url=item['url'],
        )
        await sync_to_async(_item.save)()

        return item