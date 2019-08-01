# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: directionalCoupon.py
@time: 2019/7/18 8:55
@desc:  定向优惠券
"""
import re
import time
import datetime
import requests
import win32clipboard
from PIL import Image
from io import BytesIO
from aliexpressNew.public import Public
from selenium.webdriver.common.keys import Keys
from aliExpress.public_selenium import Public_selenium
from aliexpressNew.qrCodeDiscount import QrCodeDiscount


class DirectionalCoupon(Public):
    def __init__(self, account, buyerId, value, orderId):
        self.value = value
        self.account = account
        self.buyerId = buyerId
        self.orderId = orderId
        super(DirectionalCoupon, self).__init__(self.account)

    def inquireBuyer(self):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.order.list.get'
        params = {
            '_timezone': '-8',
            # 'spm': '5261.order_list.aenewaside.1.25d53e5fpUMqc5',
            'lastSelectOrderStatus': 'all',
            'orderTab': 'Null',
            'refreshPage': 'false',
            'orderStatus': 'all',
            'filterCondition': 'OrderId,' + self.orderId,
        }
        response = requests.get(url, headers=self.headers, params=params)
        chatUrl = re.findall(re.compile(r'"https://msg.aliexpress.com/sellerMsgListNew.htm\?(.*?)"', re.S), response.text)
        return 'https://msg.aliexpress.com/sellerMsgListNew.htm?' + chatUrl[0]

    def getDiscountCode(self):
        url = 'http://py1.jakcom.it:5000/aliexpress/post/promotion/inner_coupon_code'
        data = {
            'account': self.account,
            'discount_rate': 1,
            'discount_value': self.value,
            'validity_days': 2
        }
        response = requests.post(url, data=data)
        discountCode = response.text
        print(discountCode)
        return discountCode

    def getQrCodePath(self):
        qrCodePath = QrCodeDiscount(self.account, self.value).main()
        return qrCodePath

    def clipboardImg(self, path):
        print(path)
        imagepath = path
        img = Image.open(imagepath)
        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard .OpenClipboard()  # 打开剪贴板
        win32clipboard .EmptyClipboard()  # 先清空剪贴板
        win32clipboard .SetClipboardData(win32clipboard .CF_DIB, data)  # 将图片放入剪贴板
        win32clipboard .CloseClipboard()

    def sendMessage(self, url, discountCode):
        msg = Public_selenium(url, self.account)
        msgElement = msg.browser.find_element_by_xpath('//*[@class="message-fields__autosize"]')
        msgElement.click()
        msgElement.send_keys('Congratulations, you get a %sUSD off shopping opportunity today!' % self.value)
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys('The discount code is:       (%s)' % discountCode)
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys('Enter the discount code into the order\'s remarks, and then submit the order, the system will automatically change the original price to be %sUSD off within 10 seconds' % self.value)
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys('If the order has not changed the price for a long time, please contact us.')
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys('This discount code will be expired after 30days, please as soon as possible to use it.')
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys('Have a nice day.')
        msgElement.send_keys(Keys.ENTER)
        msgElement.send_keys(':)')
        msgElement.send_keys(Keys.CONTROL + Keys.ENTER)
        msgElement.send_keys(Keys.CONTROL ,'v')
        msg.browser.find_element_by_xpath('//*[@id="_lzd-im-container"]/div/div[2]/div[2]/button[2]').click()
        # msg.action(msg).click(msgElement).perform()
        # msg.action(msg).click(msgElement).send_keys('ffff').perform()
        data = {
            'Account': self.account,
            'coupontype': '定向发放优惠券',
            'Starttime': datetime.datetime.now(),
            'activityname': '优惠码',
            'nominal_value': self.value,
            'Condition': '不限',
            'Endtime': datetime.datetime.now(),
        }
        # self.coupon_log(data)

    def main(self):
        path = self.getQrCodePath()
        self.clipboardImg(path)
        chatUrl = self.inquireBuyer()
        print(chatUrl)
        discountCode = self.getDiscountCode()
        # discountCode = '8SP3'
        self.sendMessage(chatUrl, discountCode)
        # self.createBuyerGroup()


def main(account, buyerId, orderId, value):
    directionalCoupon = DirectionalCoupon(account, buyerId, value, orderId.split('.')[1])
    directionalCoupon.main()


if __name__ == '__main__':
    account = 'fb2@jakcom.com'
    buyerId = '142829222'
    orderId = '103949862052315'
    value = 5
    main(account, buyerId, orderId, value)
