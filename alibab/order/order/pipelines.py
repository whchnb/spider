# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import requests



class OrderPipeline(object):
    # def __init__(self):
    #     self.file = open(r'D:\Main\alibaba\order\order.json', 'wb')

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), ensure_ascii=False) + ',' + "\n"
        # self.file.write(line.encode('utf-8'))
        print(item)
        url = 'http://cs1.jakcom.it/AlibabaOrderManage/ordermsg_save'
        try:
            response = requests.post(url, data=dict(item))
            print(response)
            print('订单内容', response.text)
            if response.status_code != 200 or response.json()['statusCode'] != '200':
                print('订单内容')
                print(' \033[1;35m {} \n {} \033[0m!'.format(item, response))
        except Exception as e:
            print('订单内容')
            print(' \033[1;35m {} \n {} \033[0m!'.format(item, str(e)))
        return item
