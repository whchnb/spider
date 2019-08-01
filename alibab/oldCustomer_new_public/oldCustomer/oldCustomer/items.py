# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    saleName = scrapy.Field()
    originSaleName = scrapy.Field()
    potentialScore = scrapy.Field()
    companyName = scrapy.Field()
    customerId = scrapy.Field()
    buyerID = scrapy.Field()
    aliId = scrapy.Field()
    wangwangID = scrapy.Field()
    loginId = scrapy.Field()
    referenceId = scrapy.Field()
    blueTag = scrapy.Field()
    customerGroup = scrapy.Field()
    importanceLevel = scrapy.Field()
    groupName = scrapy.Field()
    businessType = scrapy.Field()
    countryCode = scrapy.Field()
    category = scrapy.Field()
    createDate = scrapy.Field()
    customerSource = scrapy.Field()
    noteTime = scrapy.Field()
    noteContent = scrapy.Field()
    willLoss = scrapy.Field()
    isDing = scrapy.Field()
    account = scrapy.Field()



class OlderTrackingItem(scrapy.Item):
    account = scrapy.Field()
    customerId = scrapy.Field()

    companyTotalAmount = scrapy.Field()
    operaterTotalAmount = scrapy.Field()
    operaterOngoingCount = scrapy.Field()
    companyTotalCount = scrapy.Field()
    operaterTotalCount = scrapy.Field()
    companyOngoingCount = scrapy.Field()
    cycleDays = scrapy.Field()

class InfoDetailItem(scrapy.Item):
    account = scrapy.Field()
    customerId = scrapy.Field()

    annualProcurement = scrapy.Field()
    headUrl = scrapy.Field()
    business_address = scrapy.Field()
    email = scrapy.Field()
    gender = scrapy.Field()
    position = scrapy.Field()
    ims_account = scrapy.Field()
    mobilePhoneNum = scrapy.Field()
    send_name_card = scrapy.Field()


class ChatItem(scrapy.Item):
    account = scrapy.Field()
    chat_contents = scrapy.Field()
    chat_labels = scrapy.Field()
    chat_times = scrapy.Field()
    chat_types = scrapy.Field()
    Customer_md5 = scrapy.Field()


class InquiryItem(scrapy.Item):
    account = scrapy.Field()
    inquiry_contents = scrapy.Field()
    inquiry_detailSpecs = scrapy.Field()
    inquiry_labels = scrapy.Field()
    inquiry_times = scrapy.Field()
    inquiry_types = scrapy.Field()
    Customer_md5 = scrapy.Field()



