# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WatchDocument(scrapy.Item):

    _id = scrapy.Field()
    watch_uuid = scrapy.Field()
    created_at = scrapy.Field()
    body = scrapy.Field()
    source_url = scrapy.Field()
