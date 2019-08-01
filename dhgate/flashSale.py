# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: flashSale.py
@time: 2019/7/25 9:09
@desc: 限时限量
"""
import re
import time
import datetime
import requests
from urllib.parse import urlencode
from dhgate.public import Public, Main

class FlashSale(Public):
    def __init__(self, account):
        self.account = account
        super(FlashSale, self).__init__(self.account)

    def getProduct(self):
        url = 'http://cs1.jakcom.it/dhgate_promotion/limitactivity_productlist_filter'
        params = {
            'account': self.account,
            'topcount': 40
        }
        response = requests.get(url, params=params)
        productIds = [i['productId'] for i in response.json()]
        return productIds

    # 创建活动
    def createActivity(self):
        url = 'http://seller.dhgate.com/promoweb/storelimittime/saveStep1.do?'
        today = datetime.datetime.now().date()
        title = 'Daliy Special Price %s' % str(today).replace('-', '')
        startDate = str(today + datetime.timedelta(days=1)) + ' 00:00'
        endDate = str(today + datetime.timedelta(days=2)) + ' 23:59'
        data = {
            'promoDto.name': title,
            'promoDto.promoTypeId': 0,
            'startDate': startDate,
            'endDate': endDate,
            'promoDto.promoPolicy': 2,
        }
        print(data)
        headers = self.headers
        headers['Referer'] = 'http://seller.dhgate.com/promoweb/storelimittime/createStep1.do'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=headers, data=data, allow_redirects=False)
        location = response.headers['location']
        promoId = location.split('promoId=')[1].split('&')[0]
        return promoId, title, startDate, endDate

    # 确认创建
    def confirmCreate(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storelimittime/createStep2.do'
        params = {
            'promoId': promoId,
            'from': 'create'
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    # 添加产品
    def addProduct(self, promoId, productIds):
        itemcode = [('itemcodes', i) for i in productIds]
        url = 'http://seller.dhgate.com/promoweb/storelimittime/savechoose.do'
        data = [
            ('promoId', promoId),
            ('page', '1'),
            ('from', 'create'),
            ('itemcode', ''),
            ('productname', ''),
            ('searchExpireDate', ''),
            ('vip', ''),
            ('cate1PubId', ''),
            ('group1id', '')
        ]
        data.extend(itemcode)
        headers = self.headers
        headers['Referer'] = 'http://seller.dhgate.com/promoweb/storelimittime/createStep2.do?promoId=%s&from=create' %promoId
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Origin'] = 'http://seller.dhgate.com'
        response = requests.post(url, headers=headers, data=(data), allow_redirects=False)
        print(response)
        print(response.text)

    # 确认添加
    def confirmAdd(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storelimittime/createStep3.do'
        params = {
            'promoId': promoId,
            'from': 'create'
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    # 设置产品折扣 ----  可无此步
    def setProductDiscount(self, promoId, productIds):
        for productId in productIds:
            itemcodeDis = '%s_9_8.9' % productId
            url = 'http://seller.dhgate.com/promoweb/storelimittime/setprodDisforApp.do?'
            data = {
                '_t': str(time.time()).replace('.', '')[:13],
                'promoId': promoId,
                'itemcodeDis': itemcodeDis
            }
            headers = self.headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            headers['X-Requested-With'] = 'XMLHttpRequest'
            response = requests.post(url, headers=headers, data=(data))
            print(response)
            print(response.text)

    # 提交活动
    def submit(self, promoId, productIds):
        deliverData = ['%s_9_8.9_1000_1000' % i for i in productIds]
        url = 'http://seller.dhgate.com/promoweb/storelimittime/validate.do?'
        data = {
            '_t': str(time.time()).replace('.', '')[:13],
            'promoId': promoId,
            'deliverData': ','.join(deliverData),
        }
        print(data)
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        response = requests.post(url, headers=headers, data=(data))
        print(response)
        print(response.text)

    # 确认提交
    def confirmSubmit(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storelimittime/confirm.do'
        params = {
            'promoId': promoId
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    def log(self, data):
        url = 'http://cs1.jakcom.it/Dhgate_Promotion/store_activity_logger'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self):
        productIds = self.getProduct()
        productIds = [
            # '459834827',
            # '460011726',
            '462934814',
            '465710451'
        ]
        # # print(self.cookie)
        promoId, title, startDate, endDate = self.createActivity()
        print(promoId)
        self.confirmCreate(promoId)
        # promoId = 5941089
        self.addProduct(promoId, productIds)
        self.confirmAdd(promoId)
        # self.setProductDiscount(promoId, productIds)
        self.submit(promoId, productIds)
        self.confirmSubmit(promoId)
        for productId in productIds:
            logData = {
                'activity_type': '限时限量',
                'activity_name': title,
                'activity_rule': '打折',
                'time_start': startDate,
                'activity_platform': '全平台+APP专享',
                'activity_productids': productId,
                'discount_rate': '全站=9折，APP=8.9折',
                'limit_count': 1000,
                'fightgroup_stock ': 1000
            }
            self.log(logData)

def main():
    m = Main()
    accountList = m.getAcoountPwd()
    for account in accountList:
        account = 'k6tech10'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            flashSale = FlashSale(account)
            flashSale.main()
            m.bug(logName='限时限量', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='限时限量', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()