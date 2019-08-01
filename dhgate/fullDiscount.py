# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: fullDiscount.py
@time: 2019/7/25 11:48
@desc: 全店铺打折
"""
import re
import time
import string
import datetime
import requests
from dhgate.public import Public, Main


class FullDiscount(Public):
    def __init__(self, account):
        self.account = account
        super(FullDiscount, self).__init__(self.account)

    def getGroupId(self):
        url = 'http://seller.dhgate.com/promoweb/groupManage/groupList.do'
        response = requests.get(url ,headers=self.headers)
        groupId = re.findall(re.compile(r'\{"groupid":"(\d*?)","groupName":"other"\}', re.S), response.text)[0]
        return groupId

    def createActivity(self):
        groupId = self.getGroupId()
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        weekDay = datetime.datetime.now().weekday()
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        which_week = int(today) - int(start_day)
        date = '{}{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[which_week - 1], weekDay + 1)
        title = 'Store Carnival {}'.format(date)
        startDate = str(datetime.datetime.now().date() + datetime.timedelta(days=1)) + ' 00:00'
        endDate = str(datetime.datetime.now().date() + datetime.timedelta(days=1)) + ' 23:59'
        print(title)
        url = 'http://seller.dhgate.com/promoweb/storediscount/saveAllStore.do'
        data = {
            'promoGroups': 'pc-%s-9.5,app-%s-9' % (groupId, groupId),
            'errortip': 'APP专享折扣率要大于全站折扣率',
            'promoDto.name': title,
            'startDate': startDate,
            'endDate': endDate,
            'promoDto.promoPolicy': '2',
        }
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=headers, data=data)
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
            'activity_type': '全店铺打折',
            'activity_name': title,
            'time_start': startDate,
            'activity_platform': '全平台+APP专享',
            'activity_group': 'others',
            'discount_rate': '全站=9.5折，APP=9折',
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
            fullDiscount = FullDiscount(account)
            fullDiscount.main()
            m.bug(logName='全店铺打折', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='全店铺打折', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()