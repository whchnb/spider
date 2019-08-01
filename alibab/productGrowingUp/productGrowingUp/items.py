# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductgrowingupItem(scrapy.Item):
    # define the fields for your item here like:
    account = scrapy.Field()
    grow_type = scrapy.Field()  # 成长类型
    productId = scrapy.Field()  # 产品id
    grow_score = scrapy.Field()  # 成长分
    content_state = scrapy.Field()  # 内容表达状态
    effect_state = scrapy.Field()  # 效果优化状态
    service_state = scrapy.Field()  # 商品服务状态
    product_score = scrapy.Field()  # 产品信息质量分
    badreview_count = scrapy.Field()  # 差评量
    pay_buyer = scrapy.Field()  # 支付买家数
    pay_rate = scrapy.Field()  # 支付转化率
    payagain_buyer = scrapy.Field()  # 复购买家数
    delivery_ontime_rate = scrapy.Field()  # 准时发货率