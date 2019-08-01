# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductanalysisItem(scrapy.Item):
    # define the fields for your item here like:
    account = scrapy.Field()  # 账号
    productTitle = scrapy.Field()  # 产品标题
    productImgUrl = scrapy.Field()  # 产品图片
    productUrl = scrapy.Field()  # 产品链接
    productId = scrapy.Field()  # 产品id
    principal = scrapy.Field()  # 负责人
    exposureNums = scrapy.Field()  # 曝光次数
    clickNums = scrapy.Field()  # 点击次数
    visitNums = scrapy.Field()  # 访问人数
    collectionNums = scrapy.Field()  # 收藏人数
    inquiryNums = scrapy.Field()  # 询盘人数
    inquiryRate = scrapy.Field()  # 询盘率
    submitOrderNums = scrapy.Field()  # 提交订单个数
    clickRate = scrapy.Field()  # 点击率
    share = scrapy.Field()  # 分享人数
    compared = scrapy.Field()  # 对比人数
    wordSource = scrapy.Field()  # 词来源
