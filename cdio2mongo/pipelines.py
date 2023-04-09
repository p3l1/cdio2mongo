# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
import scrapy
from itemadapter import ItemAdapter
from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem

from cdio2mongo.items import WatchDocument


class MongoPipeline:

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'watches')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):

        try:
            self.db[item['watch_uuid']].insert_one(ItemAdapter(item).asdict())
            return item
        except DuplicateKeyError:
            spider.logger.warning(f"You can probably ignore this warning. Duplicate item detected: {item}")
            raise DropItem(f"Item has already been stored. Ignoring it.")
