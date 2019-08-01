# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests


class ProductinfoPipeline(object):
    def process_item(self, item, spider):
        url = 'http://cs1.jakcom.it/DhgateProductManage/productinfo_save'
        response = requests.post(url, data=dict(item))
        print(response)
        print(response.text)
        return item
