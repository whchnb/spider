# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: repeatedDistribution.py
@time: 2019/7/16 15:23
@desc: 重复铺货删除
"""
import re
import requests
from alibaba.public import Public


class RepeatedDistribution(Public):
    def __init__(self, account):
        self.account = account
        super(RepeatedDistribution, self).__init__(self.account)
        self.ctoken = self.get_ctoken()
        self.csrfToken = self.get_csrf_token()

    def deleteProduct(self, newClusterId):
        url = 'https://hz-productposting.alibaba.com/product/searchdiagnostic/repeat/product_repeat.htm'
        params = {
            'newClusterId': newClusterId
        }
        response = requests.get(url, params=params, headers=self.headers)
        productDatas = re.findall(re.compile(r'<tr>(.*?)</tr>', re.S), response.text)
        # productData = re.findall(re.compile(r'<a href="//hz-productposting.alibaba.com/product/product_detail.htm\?id=(\d*?)">\s*(.*?)</a>', re.S), response.text)
        for productData in productDatas[1:]:
            if '推荐保留' in productData:
                continue
            productDetail = re.findall(re.compile(r'<a href="//hz-productposting.alibaba.com/product/product_detail.htm\?id=(\d*?)">\s*(.*?)\s*</a>', re.S), productData)[0]
            print(productDetail)
            productId = productDetail[0]
            producttitle = productDetail[1]
            url = 'https://hz-productposting.alibaba.com/product/searchdiagnostic/repeat/product_repeat.htm?newClusterId=70816544380'
            data = {
                'action': 'searchdiagnostic/repeat/manage_product_repeat_action',
                'newClusterId': newClusterId,
                'groupId': '$query.groupId',
                'page': '1',
                'order': 'desc',
                'orderType': 'modified',
                'query': '$query.groupId',
                'delete': 'trash',
                '_csrf_token_': self.csrfToken,
                'productIds': productId,
            }
            headers = self.headers
            headers['content-type'] = 'application/x-www-form-urlencoded'
            deleteResponse = requests.post(url, data=data, headers=headers)
            print(response)
            if deleteResponse.status_code == 200:
                logData = {
                    'account': self.account,
                    'prdouctid': productId,
                    'proudctname': producttitle
                }
                self.log(logData)

    def log(self, data):
        print(data)
        url = 'http://cs1.jakcom.it/AlibabaProductManage/repeatproductdel_log'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)


    def getDeleteProductList(self):
        url = 'https://searchstaff.alibaba.com//diagnosis/order/productRepeatListAjax.do'
        params = {
            # 'callback': 'jQuery18304744515475025457_1563261921143',
            'ctoken': self.ctoken,
            # 'dmtrack_pageid': '3d86ebd20baf4d2c5d2d7bdf16bf9abe5c8cd03cfc',
            'issueType': 'duplicate_products',
            'principalId': 'all',
            'pageNo': '1',
            # '_': '1563261921326',
        }
        response = requests.get(url ,params=params, headers=self.headers)
        # print(response.url)
        total = response.json()['totalItem']
        print(total)
        pages = int(total) // 10 if int(total) % 10 == 0 else int(total) // 10 + 1
        for page in range(pages):
            response = requests.get(url, params=params, headers=self.headers)
            productList = response.json()['productList']
            for productData in productList:
                print(productData)
                newClusterId = productData['newClusterId']
                # newClusterId = 70816905164
                self.deleteProduct(newClusterId)
                # return


    def main(self):
        self.getDeleteProductList()


def main():
    account = 'fb3@jakcom.com'
    print(account)
    repeatedDistribution = RepeatedDistribution(account)
    repeatedDistribution.main()


if __name__ == '__main__':
    main()