# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: distribution.py
@time: 2019/5/15 12:19
@desc: 分销客  新增推广商品  每日上限500
"""
import sys
import time
import json
import datetime
import requests
from DynamicAnnouncement.public import Public


class Distribution(Public):

    # 类的初始化
    def __init__(self, skip):
        """
        类的初始化
        :param skip: 页码
        """
        # 继承父类Public 的init 方法
        super(Distribution, self).__init__()
        # 起始个数
        self.skip = skip * 18
        # 构造时间
        self.t = str(time.time()).replace('.', '')[:13]
        # 初始化商品id 列表
        self.product_b2bOfferIds = []
        # 获取所有商品
        self.get_all_products()

    # 获取每页的所有商品id
    def get_all_products(self):
        """
        获取每页的所有商品id
        """
        url = 'https://p4p.1688.com/cps/listOffer.html?campaignId=810167244&skip={}&limit=18&t={}&_page_csrf_token={}'.format(
            self.skip, self.t, self.t)
        response = requests.get(url, headers=self.headers, verify=False)
        data = json.loads(response.text)
        all_products = data['data']['cpsOfferVOList']
        for product in all_products:
            b2bOfferId = product['b2bOfferId']
            self.product_b2bOfferIds.append(b2bOfferId)

    # 提交
    def submit(self):
        """
        提交
        """
        data = {
            'campaignId': '810167244',
            'type': '0',
            'b2bOfferIds': self.product_b2bOfferIds,
            'categoryRatioBatch': '0.11',
            'priceFloatRatioBatch': '0',
            't': self.t,
            '_page_csrf_token': self.t
        }
        url = 'https://p4p.1688.com/cps/addAdgroup.html'
        response = requests.post(url, data=data, headers=self.headers, verify=False)
        response_data = json.loads(response.text)
        status = response_data['info']
        # 判断是否完成
        if status['ok'] == True:
            print('当前第{}页已添加完成'.format(self.skip / 18))
            self.log(self.product_b2bOfferIds)
        else:
            self.send_test_log(logName='分销客', logType='Error', msg=str(status))
            print(status)
            sys.exit()

    # 发送日志
    def log(self, productIDs):
        """
        发送日志
        :param productIDs: 商品列表
        """
        url = 'http://192.168.1.99:90/OSEE/distributionclient_Log'
        for productID in productIDs:
            data = {
                'Account': 'jakcomcom',
                'Createtime': str(datetime.datetime.now()),
                'ProductID': productID,
                'commission_rate': '0.11'
            }
            response = requests.post(url, data=data)
            print(response.text)


if __name__ == '__main__':

    for i in range(28):
        distribution = Distribution(i)
        try:
            distribution.submit()
            time.sleep(1)
            del distribution
        except Exception as e:
            distribution.send_test_log(logName='分销客', logType='Error', msg=str(e))
