# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: discountCoupon.py
@time: 2019/7/18 8:26
@desc:  领取优惠券   每日一次
@detail: 满40减3      满50减15
"""
import time
import datetime
import requests
from aliexpressNew.public import Public


class DiscountCoupon(Public):
    def __init__(self, account):
        self.account = account
        super(DiscountCoupon, self).__init__(self.account)

    def saveActivity(self, discount):
        today = datetime.datetime.now().date()
        title = discount['title'].format(str(today).replace('-', ''))
        # 构造开始时间
        today = datetime.datetime.now().date()
        startDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)) + ' 15:00:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 构造结束时间
        endDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=3)) + ' 14:59:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.voucher.save'
        data = {
            '_timezone': '-8',
            'step': '0',
            'couponType': '1',
            'grantType': '1',
            'interactiveType': '3',
            'promotionName': title,
            'startGrabHour': '7200000',
            'startStopTime': '%s,%s' % (startDate, endDate),
            'memberLevel': 'A0',
            'productScope': 'entire_shop',
            'denomination': discount['couponAmount'],
            'hasUseCondition': '1',
            'minOrderAmount': discount['standard'],
            'releasedNum': '100',
            'numPerBuyer': '2',
            'couponConsumeDateType': '1',
            'consumeValidTime': '30',
            'displayChannel': '[]'
            # 'feed': '["1"]',
            # 'freeJoin': '["1"]',
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)
        if response.json()['success'] is True:
            self.send_test_log(logName='领取型优惠券', logType='Run', msg='{} 创建成功'.format(self.account))
            data = {
                'Account': self.account,
                'coupontype': '领取型优惠券',
                'Starttime': str(today + datetime.timedelta(days=1)) + ' 15:00:00',
                'activityname': title,
                'nominal_value': discount['couponAmount'],
                'Condition': discount['standard'],
                'Endtime': str(today + datetime.timedelta(days=3)) + ' 14:59:00',
            }
            self.coupon_log(data)
        else:
            self.send_test_log(logName='领取型优惠券', logType='Error', msg='{} 创建失败 {}'.format(self.account, response.json()))

    def main(self):
        discountList = [
            {'title': 'Daily Special Coupon {}', 'couponAmount': 15, 'standard': 50},
            {'title': 'Daily Lucky Coupon {}', 'couponAmount': 3, 'standard': 40}
        ]
        for discount in discountList:
            print('--' * 50)
            try:
                self.saveActivity(discount)
            except Exception as e:
                self.send_test_log(logName='领取型优惠券', logType='Error',msg='{} 创建失败 {} {}'.format(self.account, discount, str(e)))


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
        account = 'fb2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            discountCoupon = DiscountCoupon(account)
            discountCoupon.main()
            time.sleep(3)
        except Exception as e:
            bug(logName='领取型优惠券', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()