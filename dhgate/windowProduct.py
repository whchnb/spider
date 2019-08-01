# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: windowProduct.py
@time: 2019/7/22 18:07
@desc: 橱窗
"""
import re
import requests
from dhgate.public import Public, Main


class WindowProduct(Public):
    def __init__(self, account):
        self.account = account
        super(WindowProduct, self).__init__(self.account)

    def getProductIds(self):
        url = 'http://cs1.jakcom.it/dhgate_promotion/basicpromotion_window'
        params = {
            'account': self.account,
            'topcount': 25
        }
        response = requests.get(url, params=params)
        productList = [i['productId'] for i in response.json()][:24]
        return productList

    def getSupplierid(self):
        print('获取Supplierid')
        supplierid = re.findall(re.compile(r'supplierid=(.*?);'), self.cookie)[0]
        return supplierid

    def getSellerswindowids(self):
        url = 'http://seller.dhgate.com/store/storeWindowManage.do'
        response = requests.get(url, headers=self.headers)
        sellerswindowids = re.findall(re.compile(r'onclick="changePage\(\'(.*?)\'\).*?\s*<span\sclass="j-caseName"\s?>(.*?)\s*?\(', re.S), response.text)
        storeid = re.findall(re.compile(r'id="storeid" value="(.*?)"', re.S), response.text)[0]
        return sellerswindowids, storeid

    def getTotalCounts(self, sellerswindowid, storeid):
        url = 'http://seller.dhgate.com/store/storeWindowManage.do'
        data = {
            'pagenum': 1,
            'pagesize': 10,
            'page': 1,
            'sellerswindowid': sellerswindowid[0],
            'shopwindowid': 101,
            'sellerwindowroleid': '',
            'shopwinName': '',
            'autofill': '',
            'optType': '',
            'showNum': '',
            'showFlag': '',
            'currentnum': 8,
            'swindowproductid': '',
            'storeid': storeid,
            'ifshowguide': 1,
        }
        response = requests.post(url, headers=self.headers, data=data)\
        # print(self.headers)
        totalCounts = re.findall(re.compile(r'<span class="tips-warning">.*?(\d*?)</span>', re.S), response.text)[0]
        alreadyUploadProducts = re.findall(re.compile(r'name="storeproduct" value="(.*?)"', re.S), response.text)
        print(alreadyUploadProducts)
        return totalCounts, alreadyUploadProducts

    def removeProduct(self, storeproduct, sellerswindowid, storeid):
        url = 'http://seller.dhgate.com/store/removeProToWindow.do?dhpath=08,0803'
        data = {
            'storeproduct': storeproduct,
            'pagenum': '1',
            'pagesize': '10',
            'page': '1',
            'sellerswindowid': sellerswindowid[0],
            'shopwindowid': '100',
            'sellerwindowroleid': '',
            'shopwinName': sellerswindowid[1],
            'autofill': '',
            'optType': '',
            'showNum': '',
            'showFlag': '',
            'currentnum': '3',
            'swindowproductid': '',
            'storeid': storeid,
            'ifshowguide': '1'
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)

    def addProduct(self, sellerswindowid, supplierid, productId):
        url = 'http://seller.dhgate.com/store/addproToWindow.do'
        data = {
            'windowId': sellerswindowid[0],
            'windowType': '100',
            'cursupplierid': supplierid,
            'itemcode': str(productId) + ',',
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        if response.status_code == 200:
            self.log(sellerswindowid, productId)

    def log(self, sellerswindowid, productIds):
        url = 'http://cs1.jakcom.it/dhgate_promotion/window_logger'
        for productId in productIds.split(','):
            data = {
                'account': self.account,
                'windowId': sellerswindowid[0],
                'productId': productId,
                'type': sellerswindowid[1]
            }
            response = requests.post(url, data=data)
            print(response)
            print(response.text)

    def main(self):
        productIdList = self.getProductIds()
        print(productIdList)
        if len(productIdList) == 0:
            raise IndexError('%s 没有获取到商品' % self.account)
        supplierid = self.getSupplierid()
        sellerswindowids, storeid = self.getSellerswindowids()
        for index, sellerswindowid in enumerate(sellerswindowids):
            for i in range(2):
                totalCounts, alreadyUploadProducts = self.getTotalCounts(sellerswindowid, storeid)
                for storeproduct in alreadyUploadProducts:
                    # storeproduct = '477833612_ff80808169b50815016c19246c061c93'
                    # productId = storeproduct.split('_')[0]
                    self.removeProduct(storeproduct, sellerswindowid, storeid)
            productIds = ','.join(productIdList[index * 8: (index + 1) * 8])
            self.addProduct(sellerswindowid, supplierid, productIds)


def main():
    m = Main()
    accountList = m.getAcoountPwd()
    for account in accountList:
        # account = 'jakcomdh'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            windowProduct = WindowProduct(account)
            windowProduct.main()
            m.bug(logName='敦煌橱窗产品', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            pass
            m.bug(logName='敦煌橱窗产品', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()