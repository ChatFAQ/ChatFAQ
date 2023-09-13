# -*- coding: utf-8 -*-
from back.apps.language_model.models import KnowledgeBase, KnowledgeItem
from channels.db import database_sync_to_async
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class GenericPipeline(object):
    kb = None

    async def process_item(self, item, spider):
        if not self.kb:
            self.kb = await database_sync_to_async(KnowledgeBase.objects.get)(id=spider.knowledge_base_id)

        _item = await database_sync_to_async(KnowledgeItem.objects.create)(
            knowledge_base=self.kb,
            title=item['title'],
            content=item['content'],
            #context=item['section'],
            url=item['url'],
        )
        await database_sync_to_async(_item.save)()

        return item
