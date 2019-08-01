# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: popularCoupon.py
@time: 2019/7/18 9:47
@desc:  聚人气优惠券
"""
import time
import string
import datetime
import requests
from aliexpressNew.public import Public


class PopularCoupon(Public):
    def __init__(self, account):
        self.account = account
        super(PopularCoupon, self).__init__(self.account)

    def saveActivity(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        wihch_week = int(today) - int(start_day)
        date = '{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[wihch_week])
        title = 'Hot Coupon {}'.format(date)
        today = datetime.datetime.now().date()
        # 活动开始时间
        startDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)) + ' 15:00:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 活动结束时间
        endDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=8)) + ' 14:59:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 优惠券使用开始时间
        couponStartDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)) + ' 15:00:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 优惠券使用结束时间
        couponEndDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=31)) + ' 14:59:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.voucher.save'
        data = {
            '_timezone': '-8',
            'step': '0',
            'couponType': '3',
            'grantType': '1',
            'interactiveType': '5',
            'promotionName': title,
            'startGrabHour': '7200000',
            'startStopTime': '%s,%s' % (startDate, endDate),
            'memberLevel': 'A0',
            'productScope': 'entire_shop',
            'denomination': '2',
            'hasUseCondition': '0',
            'minOrderAmount': '',
            'releasedNum': '1000',
            'numPerBuyer': '1',
            'couponConsumeDateType': '2',
            'consumeTimeRange': '%s,%s' % (couponStartDate, couponEndDate),
            'displayChannel': '[]'
            # 'feed': '["1"]',
            # 'freeJoin': '["1"]',
        }
        response = requests.post(url ,headers=self.headers, data=data)
        print(response)
        print(response.text)
        if response.json()['success'] is True:
            self.send_test_log(logName='聚人气优惠券', logType='Run', msg='{} 创建成功'.format(self.account))
            data = {
                'Account': self.account,
                'coupontype': '聚人气优惠券',
                'Starttime': str(today + datetime.timedelta(days=1)) + ' 15:00:00',
                'activityname': title,
                'nominal_value': 2,
                'Condition': '不限',
                'Endtime': str(today + datetime.timedelta(days=8)) + ' 14:59:00',
            }
            self.coupon_log(data)
        else:
            self.send_test_log(logName='聚人气优惠券', logType='Error', msg='{} 创建失败 {}'.format(self.account, response.json()))

    def main(self):
        try:
            self.saveActivity()
        except Exception as e:
            self.send_test_log(logName='聚人气优惠券', logType='Error', msg='{} 创建失败 {}'.format(self.account, str(e)))

# 获取速卖通全部账号
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
    for account in accountList[:1]:
        # account = 'fb2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            popularCoupon = PopularCoupon(account)
            popularCoupon.main()
            time.sleep(3)
        except Exception as e:
            bug(logName='聚人气优惠券', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()