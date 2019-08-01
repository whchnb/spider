# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: trafficExpress.py
@time: 2019/7/22 19:10
@desc: 流量快车
"""
import re
import time
import requests
from dhgate.public import Public, Main


class TrafficExpress(Public):
    def __init__(self, account):
        self.account = account
        super(TrafficExpress, self).__init__(self.account)

    def getTotalCount(self):
        url = 'http://seller.dhgate.com/marketweb/trafficbus/pageload.do'
        response = requests.get(url, headers=self.headers)
        totalCount = re.findall(re.compile(r'<strong class="f14weight green">(\d*?)</strong>', re.S), response.text)[0]
        alreadyProductIds = re.findall(re.compile(r'<tr itemcode="(.*?)">', re.S), response.text)
        return totalCount, alreadyProductIds

    def getProduct(self):
        url = 'http://cs1.jakcom.it/dhgate_promotion/basicpromotion_flow'
        params = {
            'account': self.account,
            'topcount': 15
        }
        response = requests.get(url, params=params)
        productIds = [i['productId'] for i in response.json()][:3]
        print(productIds)
        return productIds

    def addProduct(self, productIdList):
        url = 'http://seller.dhgate.com/marketweb/trafficbus/saveprod.do'
        data = {
            'itemcodes': ','.join(productIdList)
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)
        if response.json()['flag'] is True:
            self.log(productIdList)

    def removeProduct(self, productId):
        url = 'http://seller.dhgate.com/marketweb/trafficbus/cancle.do'
        params = {
            'itemcodes': productId,
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)
        print(response.text)

    def log(self, productIdList):
        url = 'http://cs1.jakcom.it/dhgate_promotion/flow_logger'
        for productId in productIdList:
            data = {
                'account': self.account,
                'productId': productId
            }
            response = requests.post(url, data=data)
            print(response)
            print(response.text)

    def main(self):
        productIdList = self.getProduct()
        if len(productIdList) == 0:
            raise IndexError('%s 没有获取到产品' % self.account)
        totalCount, alreadyProductIds = self.getTotalCount()
        print(totalCount, alreadyProductIds)
        if int(totalCount) > 0:
            for productId in alreadyProductIds:
                self.removeProduct(productId)
        self.addProduct(productIdList)


def main():
    m = Main()
    accountList = m.getAcoountPwd()
    print(accountList)
    for account in accountList[-10:]:
        print('**' * 50)
        print(account)
        print('**' * 50)
        if account == 'jakcomdh':
            continue
        try:
            trafficExpress = TrafficExpress(account)
            trafficExpress.main()
            m.bug(logName='敦煌流量快车', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            pass
            m.bug(logName='敦煌流量快车', logType='Error', msg='%s %s' % (account, str(e)))



if __name__ == '__main__':
    main()