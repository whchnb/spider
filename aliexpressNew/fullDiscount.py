# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: fullDiscount.py
@time: 2019/7/18 8:12
@desc:  满立减
"""
import time
import json
import datetime
import requests
from aliexpressNew.public import Public


class FullDiscount(Public):
    def __init__(self, account):
        self.account = account
        super(FullDiscount, self).__init__(self.account)

    def saveActivity(self):
        today = datetime.datetime.now().date()
        title = 'Wholesale Discount {}'.format(str(today).replace('-', ''))
        # 构造开始时间
        today = datetime.datetime.now().date()
        startDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)) + ' 15:00:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 构造结束时间
        endDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=3)) + ' 14:59:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.shop.save'
        data = {
            '_timezone': '-8',
            'step': '0',
            'promotionName': title,
            'promotionTime': '%s,%s' % (startDate, endDate),
            'promotionType': 'fixedDiscount',
            'promotionScope': 'entire_shop',
            'fixedDiscountTiers': json.dumps([
                {
                    "criteria":{"type":"amount","value":"10"},
                    "offering":{"type":"decreaseMoney","value":"1"},
                    "extra":{"type":"checkbox","value":False}
                },{
                    "criteria":{"type":"amount","value":"20"}
                    ,"offering":{"type":"decreaseMoney","value":"3"}
                },{
                    "criteria":{"type":"amount","value":"30"},
                    "offering":{"type":"decreaseMoney","value":"5"}
                }
            ])
        }
        print(data)
        response = requests.post(url, headers=self.headers, data=data)
        if  response.json()['success'] is True:
            self.send_test_log(logName='满立减', logType='Run', msg='{} 创建成功'.format(self.account))
            logData = {
                'Account': self.account,
                'Promotion_type': '满立减',
                'Channel': '自建活动',
                'Promotion_Name': title,
                'Begin_time': str(today + datetime.timedelta(days=1)) + ' 15:00:00',
                'End_time': str(today + datetime.timedelta(days=3)) + ' 14:59:00',
                'ProductID': '1',
            }
            self.log(logData)
        else:
            self.send_test_log(logName='满立减', logType='Error',msg='{} {}'.format(self.account, response.json()))

    def main(self):
        try:
            self.saveActivity()
        except Exception as e:
            self.send_test_log(logName='满立减', logType='Error', msg='{} {}'.format(self.account, str(e)))


def getAccount():
    url = 'http://py2.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def bug(logName, msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.160:90/Log/Write'
    data = {
        'LogName': logName,
        'LogType': 'Running Failed',
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)


def main():
    accountList = getAccount()
    accountList = [
        # 'leliu2@jakcom.com',
        'leliu1@jakcom.com',
        'dongtian3@jakcom.com',
        'jikong3@jakcom.com',
        'dongtian2@jakcom.com',
        'jikong2@jakcom.com',
        'jikong1@jakcom.com',

    ]
    for account in accountList:
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            fullDiscount = FullDiscount(account)
            fullDiscount.main()
            # time.sleep(3)
        except Exception as e:
            bug(logName='满立减', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()