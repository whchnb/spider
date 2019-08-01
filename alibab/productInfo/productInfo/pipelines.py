# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import requests


class ProductinfoPipeline(object):
    # def __init__(self):
    #     self.file = open(r'D:\Main\alibaba\productInfo\productInfo.json', 'wb')

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), ensure_ascii=False) + ',' + "\n"
        # self.file.write(line.encode('utf-8'))
        url = 'http://cs1.jakcom.it/AlibabaProductManage/productinfo_save'
        response = requests.post(url, data=dict(item))
        print(response)
        print(response.text)
        if response.json()['statusCode'] == '300':
            print(item)
        return item
