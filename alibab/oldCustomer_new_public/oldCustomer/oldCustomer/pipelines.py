# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
from oldCustomer.items import InfoItem, ChatItem, InquiryItem, OlderTrackingItem, InfoDetailItem



class OldcustomerPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, InfoItem) or isinstance(item, OlderTrackingItem) or isinstance(item, InfoDetailItem):
            # a = dict(item)
            # print(a)
            info_url = 'http://192.168.1.160:90/AlibabaCustomerInfo/customerinfo_save'
            try:
                response = requests.post(info_url, data=dict(item))
                if isinstance(item, InfoItem):
                    print(response)
                    print('客户信息', item['account'], item['countryCode'], response.text)
                else:
                    print(response)
                    print('客户信息', item['account'], response.text)
            except:
                print('客户信息')
                print(' \033[1;35m {} \033[0m!'.format(item))
        if isinstance(item, ChatItem):
            info_url = 'http://192.168.1.160:90/AlibabaCustomerInfo/customer_chat_save'
            try:
                response = requests.post(info_url, data=dict(item))
                print(response)
                print('聊天内容', response.text)
            except:
                print('聊天内容')
                print(' \033[1;35m {} \033[0m!'.format(item))
        if isinstance(item, InquiryItem):
            info_url = 'http://192.168.1.160:90/AlibabaCustomerInfo/customer_inquiry_save'
            try:
                response = requests.post(info_url, data=dict(item))
                print(response)
                print('询盘内容', response.text)
            except:
                print('询盘内容')
                print(' \033[1;35m {} \033[0m!'.format(item))
        return item
