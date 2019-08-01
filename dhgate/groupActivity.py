# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: groupActivity.py
@time: 2019/7/23 15:59
@desc: 拼团活动
"""
import re
import time
import json
import string
import datetime
import requests
from dhgate.public import Public, Main
from urllib.parse import urlencode


class GroupActivity(Public):
    def __init__(self, account):
        self.account = account
        super(GroupActivity, self).__init__(self.account)
        self.getPrice()
        self.getCounts()

    def getPrice(self):
        url = 'http://cs1.jakcom.it/alibaba/Get_prices'
        response = requests.get(url)
        self.priceDict = {i['sku']: i['wholesale_5_usd'] for i in eval(response.text)}

    def getCounts(self):
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep1.do?ptype=1'
        response = requests.get(url, headers=self.headers)
        self.count = re.findall(re.compile(r'<div class="totalnums clearfix margtop15">\s*.*?class="fcf50">\s*?(\d*?)\s*?</span>', re.S), response.text)
        print(self.count)

    def getProductDatas(self, counts):
        url = 'http://cs1.jakcom.it/dhgate_promotion/activity_productlist_filter'
        params = {
            'account': self.account,
            'topcount': counts
        }
        response = requests.get(url, params=params)
        productIdList = [{'id':i['productId'], 'sku':i['sku']} for i in response.json() if i['sku'] is not None]
        print(productIdList)
        return productIdList

    # 创建活动
    def createActivity(self):
        print('创建活动')
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep1.do?ptype=1'
        response = requests.get(url, headers=self.headers)
        counts = re.findall(re.compile(r'<div class="totalnums clearfix margtop15">\s*.*?class="fcf50">\s*?(\d*?)\s*?</span>', re.S), response.text)[0]
        if int(counts) <= 0:
            return False, False, False
        productIdList = self.getProductDatas(counts)
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        which_week = int(today) - int(start_day)
        date = '{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[which_week - 1])
        title = 'Weekly Groupon {}'.format(date)
        startDate = datetime.datetime.now().date() + datetime.timedelta(days=3)
        endDate = startDate + datetime.timedelta(days=60)
        stepUrl1 = 'http://seller.dhgate.com/promoweb/storeteamshopping/saveStep1.do'
        data = {
            'promoDto.name': title,
            'startDate': '%s 00:00' % startDate,
            'endDate': '%s 00:00' % endDate,
            'promoDto.promoPolicy': 1,
        }
        headers = self.headers
        headers['Referer'] = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep1.do?dhpath=10004,30,3005'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Host'] = 'seller.dhgate.com'
        response = requests.post(stepUrl1, headers=headers, data=(data), allow_redirects=False)
        promoId = response.headers['location'].split('promoId=')[1].split('&')[0]
        print(response.headers)
        print(response)
        print(response.text)
        print(promoId)
        return title, startDate, endDate, promoId, productIdList

    # 确认创建
    def confirmCreate(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep2.do'
        params = {
            'promoId': promoId,
            'from': 'create'
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    # 添加产品
    def addProducts(self, promoId, productIdList):
        print('添加产品')
        itemcode = [('itemcodes', i['id']) for i in productIdList]
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/savechoose.do'
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
        headers['Referer'] = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep2.do?promoId=%s&from=create' % promoId
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Origin'] = 'http://seller.dhgate.com'
        response = requests.post(url, headers=headers, data=(data), allow_redirects=False)
        print(response)
        print(response.text)

    # 确认添加
    def confirmAdd(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/createStep3.do'
        params = {
            'promoId': promoId,
            'from': 'create'
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    # 发布
    def submit(self, promoId, productIdList):
        print('发布')
        deliverData = ['%s__%s_1000_500_2'% (i['id'], self.priceDict[i['sku']]) for i in productIdList]
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/validate.do?'
        data = {
            '_t': str(time.time()).replace('.', '')[:13],
            'promoId': promoId,
            'deliverData': ','.join(deliverData)
        }
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        response = requests.post(url, headers=headers, data=(data))
        print(response)
        print(response.text)
        print(data)

    # 确认发布
    def confirmSubmit(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/storeteamshopping/confirm.do'
        params = {
            'promoId': promoId,
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response)

    def log(self, data):
        url = 'http://cs1.jakcom.it/Dhgate_Promotion/store_activity_logger'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)


    def main(self):
        # self.getProductDatas(100)
        # self.getPrice()
        title, startDate, endDate, promoId, productIdList = self.createActivity()
        # promoId = 5935740
        print(promoId)
        self.confirmCreate(promoId)
        # productIdList = [
        #     {'id': '433903633', 'sku': 'R3'},
        #     {'id': '445301164', 'sku': 'R3'},
        #     ]
        self.addProducts(promoId, productIdList)
        self.confirmAdd(promoId)
        self.submit(promoId, productIdList)
        self.confirmSubmit(promoId)
        for productId in productIdList:

            logData = {
                'activity_type': '拼团',
                'activity_name': title,
                'time_start': startDate,
                'activity_duration': 60,
                'activity_productids': productId['id'],
                'fightgroup_price': self.priceDict[productId['sku']],
                'fightgroup_peoples': 2,
                'limit_count': 500,
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
            groupActivity = GroupActivity(account)
            groupActivity.main()
            m.bug(logName='拼团活动', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='拼团活动', logType='Error', msg='%s %s' % (account, str(e)))

if __name__ == '__main__':
    main()