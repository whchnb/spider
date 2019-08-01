# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: fullReduction.py
@time: 2019/7/25 12:15
@desc: 全店铺满减
"""
import re
import time
import string
import datetime
import requests
from dhgate.public import Public, Main


class FullReduction(Public):
    def __init__(self, account):
        self.account = account
        super(FullReduction, self).__init__(self.account)

    def createActivity(self):
        url = 'http://seller.dhgate.com/promoweb/fullreduceacty/saveActy.do'
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        which_week = int(today) - int(start_day)
        date = '{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[which_week - 1])
        title = 'Store Discount {}'.format(date)
        startDate = str(datetime.datetime.now().date() + datetime.timedelta(days=1))
        endDate = str(datetime.datetime.now().date() + datetime.timedelta(days=10))
        data = {
            'promoFullReductionDto.name': title,
            'promoFullReductionDto.startDate': startDate,
            'startDate': startDate + ' 00:00',
            'promoFullReductionDto.endDate': endDate,
            'endDate': endDate + ' 23:59',
            'promoFullReductionDto.full': '20',
            'promoFullReductionDto.reduction': '2',
            'accumulate': 'on',
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)
        return title, startDate, endDate


    def log(self, data):
        url = 'http://cs1.jakcom.it/Dhgate_Promotion/store_activity_logger'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self):
        title, startDate, endDate = self.createActivity()
        logData = {
            'activity_type': '全店铺满减',
            'activity_name': title,
            'time_start': startDate + ' 00:00',
            'activity_rule': '满20 减 2，优惠可累加'
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
            fullReduction = FullReduction(account)
            fullReduction.main()
            m.bug(logName='全店铺满减', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='全店铺满减', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()