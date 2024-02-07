# -*- coding: utf-8 -*-
from back.apps.language_model.models.data import DataSource, KnowledgeItem
from channels.db import database_sync_to_async
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class GenericPipeline(object):
    ds = None

    async def process_item(self, item, spider):
        if not self.ds:
            self.ds = await database_sync_to_async(DataSource.objects.select_related('knowledge_base').get)(id=spider.data_source_id)

        _item = await database_sync_to_async(KnowledgeItem.objects.create)(
            data_source=self.ds,
            knowledge_base=self.ds.knowledge_base,
            title=item['title'],
            content=item['content'],
            # context=item['section'],
            url=item['url'],
        )
        await database_sync_to_async(_item.save)()

        return item
