# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: mainPush.py
@time: 2019/7/18 13:15
@desc: 主推计划
"""
import json
import datetime
import requests
import xmltodict
from aliexpressNew.public import Public


class MainPush(Public):
    def __init__(self, account):
        self.account = account
        super(MainPush, self).__init__(self.account)
        self.csrfToken = self.get_csrf_token()

    # 获取添加的商品
    def addProducts(self):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/getproducts_hotsale?topcount=60&account=' + self.account
        response = requests.get(url)
        productIdList = [i['Product_ID'] for i in response.json()]
        return productIdList

    # 获取正在计划中的商品
    def onlineProducts(self):
        url = 'https://afseller.aliexpress.com/affiliate/productCommission/listProductCommission.do'
        params = {
            'isHot': True,
            'pageSize': '50',
            'validIndex': '1',
            'invalidIndex': '1',
        }
        response = requests.get(url, headers=self.headers, params=params)
        xmlparse = xmltodict.parse(response.text)
        jsonstr = json.dumps(xmlparse, indent=1)
        datas = json.loads(jsonstr)['ResponseResult']['data']
        # print(datas)
        foreverProductDatas = datas['afSellerPromotionProduct'] if isinstance(datas['afSellerPromotionProduct'], list) else [datas['afSellerPromotionProduct']]
        expiredProductDatas = datas['expiringAfSellerPromotionProduct'] if isinstance(datas['expiringAfSellerPromotionProduct'], list) else [datas['expiringAfSellerPromotionProduct']]
        foreverProductIdList = [i['productId'] for i in foreverProductDatas]
        expiredProductIdList = [i['productId'] for i in expiredProductDatas]
        return foreverProductIdList, expiredProductIdList

    def main(self):
        productIdList = self.addProducts()
        print(productIdList)


def main():
    account = 'fb2@jakcom.com'
    mainPush = MainPush(account)
    mainPush.main()


if __name__ == '__main__':
    main()