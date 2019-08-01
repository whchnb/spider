# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: qrCodeDiscount.py
@time: 2019/7/26 16:53
@desc:
"""
import time
import datetime
import requests
from aliexpressNew.public import Public


class QrCodeDiscount(Public):
    def __init__(self, account, value):
        self.account = account
        self.value = value
        super(QrCodeDiscount, self).__init__(self.account)

    def createDiscount(self):
        title = '$%s USD Coupon %s' % (self.value, str(time.time()).split('.')[0])
        # 构造开始时间
        today = datetime.datetime.now()
        startDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(minutes=2)).split('.')[0], "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 构造结束时间
        endDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=30)).split('.')[0], "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        print(title)
        print(startDate)
        print(endDate)
        print(str(time.time()).split('.')[0] + '000')
        print(str(int(str(time.time()).split('.')[0]) + 2) + '000')
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.voucher.save'
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
        headers['x-csrf'] = self.get_csrf_token()
        data = {
            '_timezone': '-8',
            'spm': '5261.promotion_index.0.0.3bc13e5fZlm1tT',
            'step': '0',
            'couponType': '2',
            'grantType': '2',
            'interactiveType': '3',
            # 'startStopTime': '%s,%s' % (str(time.time()).split('.')[0] + '000', endDate),
            'promotionName': title,
            'startGrabHour': '7200000',
            'memberLevel': 'A0',
            'productScope': 'entire_shop',
            'denomination': self.value,
            'hasUseCondition': '0',
            'minOrderAmount': '',
            'releasedNum': '1',
            'numPerBuyer': '1',
            'couponConsumeDateType': '2',
            'consumeTimeRange': '%s,%s' % (startDate, endDate),
            # 'consumeTimeRange': '1564124400000,1564297199000',
            'displayChannel': '[]',
        }
        response = requests.post(url, headers=headers, data=data)
        print(response)
        print(response.text)
        return title, startDate, endDate

    def getQrCodeUrl(self, title):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.voucher.list'
        params = {
            '_timezone': '-8',
            'type': '2',
            'status': 'releasing',
            'current': '1',
            'total': '30',
            'pageSize': '10',
        }
        response = requests.get(url, headers=self.headers, params=params)
        datas = response.json()['data']['modules'][0]['dataSource']
        for data in datas:
            if data['campaignName']['title'] == title:
                qrCodeUrl = data['action'][3]['value']
                return qrCodeUrl

    def downLoadQrCode(self, qrCodeUrl, title):
        strTime = title.split(' ')[-1]
        response = requests.get(qrCodeUrl)
        path = r'\\192.168.1.98\公共共享盘\@ Code\速卖通定向二维码\临时码\%s_%s_%s.png' % (self.account, self.value, strTime)
        with open(path, 'ab') as f:
            f.write(response.content)
            f.close()
        return path

    def main(self):
        title, startDate, endDate = self.createDiscount()
        # title = '$5 USD Coupon 1564207712'
        qrCodeUrl = self.getQrCodeUrl(title)
        path = self.downLoadQrCode(qrCodeUrl, title)
        # logData = {
        #     'Account': self.account,
        #     'coupontype': '定向优惠券',
        #     'Starttime': startDate,
        #     'activityname': title,
        #     'nominal_value': self.value,
        #     'Condition': '无',
        #     'Endtime': endDate,
        # }
        # self.coupon_log(logData)
        # path = r'\\192.168.1.98\公共共享盘\@ Code\速卖通定向二维码\临时码\fb2@jakcom.com_5_1564207712.png'
        print(path)
        return path


def main():
    value = 5
    account = 'fb2@jakcom.com'
    qrCodeDiscount = QrCodeDiscount(account, value)
    qrCodeDiscount.main()


if __name__ == '__main__':
    main()