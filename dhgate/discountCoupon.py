# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: discountCoupon.py
@time: 2019/7/25 12:54
@desc: 领取型优惠券
"""
import re
import time
import string
import datetime
import requests
from dhgate.public import Public, Main


class DiscountCoupon(Public):
    def __init__(self, account):
        self.account = account
        super(DiscountCoupon, self).__init__(self.account)

    def createCoupon(self):
        url = 'http://seller.dhgate.com/promoweb/coupon/save.do'
        today = datetime.datetime.now()
        title = 'Daliy Coupon %s' % str(today.date()).replace('-', '')
        startDate = today + datetime.timedelta(days=1)
        endDate = today + datetime.timedelta(days=30)
        issueAmount = startDate.day + 1
        orderAmount = issueAmount * 10
        data ={
            'type': '7',
            'campaignid': '',
            'buyerlist': '',
            'campaignname': title,
            'startDate': str(startDate),
            'startHour': '00:00',
            'endDate': str(endDate),
            'endHour': '23:59',
            'policy': '2',
            'platform_all_app': '0',
            'amount': issueAmount,
            'amountM': issueAmount + 1,
            'ccount': '999',
            'ccountM': '999',
            'orderAmo': orderAmount,
            'validday_type': '0',
            'validday': '30',
            'validdayStartDate': '',
            'validdayStartHour': '00:00',
            'validdayEndDate': '',
            'validdayEndHour': '23:59',
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)
        return title, startDate, issueAmount, orderAmount

    def log(self, data):
        url = 'http://cs1.jakcom.it/Dhgate_Promotion/store_activity_logger'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self):
        title, startDate, issueAmount, orderAmount = self.createCoupon()
        logData = {
            'activity_type': '领取型优惠券',
            'activity_name': title,
            'time_start': startDate,
            'activity_platform': '全平台+APP专享',
            'activity_rule': '全站= %s; APP= %s' % (issueAmount, issueAmount + 1),
            'quantity': '全站=999，APP=999',
            'activity_duration': orderAmount,
            'limit_count': 30
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
            discountCoupon = DiscountCoupon(account)
            discountCoupon.main()
            m.bug(logName='领取型优惠券', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='领取型优惠券', logType='Error', msg='%s %s' % (account, str(e)))

if __name__ == '__main__':
    main()