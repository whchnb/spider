# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductinfoItem(scrapy.Item):
    # define the fields for your item here like:
    account = scrapy.Field()    # 账号
    categoryId = scrapy.Field()    # 类目
    productThumbnail = scrapy.Field()  # 缩略图
    productTitle = scrapy.Field()  # 产品标题
    minPrice = scrapy.Field()  # 最低价
    maxPrice = scrapy.Field()  # 最高价
    priceUnit = scrapy.Field()  # 价格单位
    principal = scrapy.Field()  # 负责人
    updateDate = scrapy.Field()  # 更新时间
    productDetailUrl = scrapy.Field()  # 商品详情链接
    finalScore = scrapy.Field()  # 产品得分
    productLevel = scrapy.Field()  # 产品等级
    productStatus = scrapy.Field()  # 产品状态
    showNum = scrapy.Field()  # 月曝光量
    clickNum = scrapy.Field()  # 月点击量
    fbNum = scrapy.Field()  # 月反馈量
    redModel = scrapy.Field()  # 型号
    groupName = scrapy.Field()  # 分组
    productId = scrapy.Field()  # 产品id
    exportDate = scrapy.Field()  # 出口时间
    exportRebateRate = scrapy.Field()  # 出口回扣率
    exportId = scrapy.Field()  # 出口id
    exportModel = scrapy.Field()  # 出口型号
    exportName = scrapy.Field()  # 出口名称
    exportStatus = scrapy.Field()  # 出口状态
    exportServiceName = scrapy.Field()  # 产品服务类型
    productKeyWords = scrapy.Field()  # 关键词
    productPublishUrl = scrapy.Field()  # 产品审核链接
    productModifyUrl = scrapy.Field()  # 产品修改链接
