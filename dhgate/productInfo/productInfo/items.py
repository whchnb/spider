# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductinfoItem(scrapy.Item):
    # define the fields for your item here like:
    account = scrapy.Field()
    productId = scrapy.Field()
    subject = scrapy.Field()
    productUrl = scrapy.Field()
    score = scrapy.Field()
    groupName = scrapy.Field()
    ordercount = scrapy.Field()
    validity = scrapy.Field()
