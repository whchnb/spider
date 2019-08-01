# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: changePrice.py
@time: 2019/7/12 14:41
@desc: 速卖通自动改价
"""
import re
import time
import json
import datetime
import requests
import threading
from selenium import webdriver
from urllib.parse import urljoin
from aliexpressNew.public import Public
from selenium.webdriver.chrome.options import Options


class ChangePrice(Public):
    def __init__(self, account):
        self.account = account
        super(ChangePrice, self).__init__(self.account)
        # self.setCookie()

    def setCookie(self, orderId):
        url = 'https://gsp.aliexpress.com/apps/order/index'
        url = 'https://trade.aliexpress.com/order_detail.htm?orderId=' + orderId
        # url = 'https://trade.aliexpress.com/issue/issue_list.htm'
        response = requests.get(url, headers=self.headers)
        # print(response.headers)
        setCookie = response.headers['set-cookie']
        # print(setCookie)
        # # try:
        # intl_common_forever = re.findall(re.compile(r'intl_common_forever=(.*?);'), setCookie)[0]
        ASDIAGNOSIS = re.findall(re.compile(r'ASDIAGNOSIS=(.*?);'), setCookie)[0]
        _mle_tmp_new0 = re.findall(re.compile(r'_mle_tmp_new0=(.*?);'), setCookie)[0]
        self.cookie = self.cookie + ';ASDIAGNOSIS={};_mle_tmp_new0={}'.format(ASDIAGNOSIS, _mle_tmp_new0)
        self.headers['cookie'] = self.cookie
        # except Exception as e:
        #     self.send_test_log(logName='速卖通改价', logType='Error', msg='%s cookie 设置出错 %s' % (self.account, str(e)))

    # 获取csrfToken
    def getCsrfToken(self, orderId):
        url = 'https://trade.aliexpress.com/order_detail.htm?orderId={}&discount_list=true'.format(orderId)
        response = requests.get(url, headers=self.headers)
        # print(response.text)
        csrfToken = re.findall(re.compile(r"<input name='_csrf_token' type='hidden' value='(.*?)'>", re.S), response.text)[0]
        return csrfToken

    def getPayAmount(self, url):
        response = requests.get(url, headers=self.headers)
        totalAmount = re.findall(re.compile(r'<td class="order-price">\s*?.*?([\d,\.]*?)\s*?</td>', re.S), response.text)[0].replace(',', '')
        productAmount = re.findall(re.compile(r'<td class="product-price">\s*?.*?([\d,\.]*?)\s*?</td>', re.S), response.text)[0].replace(',', '')
        return float(totalAmount), float(productAmount)

    # 获取订单id
    def getOrderId(self):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.order.list.get'
        params = {
            '_timezone': '-8',
            'lastSelectOrderStatus': '100',
            'orderTab': 'Unpaid',
            'refreshPage': 'false',
            'orderStatus': '100',
            'filterCondition': 'OrderId',
            'current': '1',
            'total': '3',
            'pageSize': '10',
        }
        response = requests.get(url, headers=self.headers, params=params)
        # print(response.json())
        orderDatas = response.json()['data']['modules'][3]['dataSource']
        # if len(orderDatas) != 0:
        #     self.orderPayCountdownSelenium = OrderPayCountdownSelenium(self.cookie, 'https://gsp.aliexpress.com/apps/order/index')
        for orderData in orderDatas:
            # import json
            # print(json.dumps(orderData, ensure_ascii=False))
            # print(orderData)
            orderUrl = orderData['children'][0]['orderInfo'][0]['href']
            orderId = orderData['children'][0]['orderInfo'][0]['content']
            remark = ' '.join(re.findall(re.compile(r"'<font color=.*?>.*?([\d\w]*?)</font>'", re.S), str(orderData)))
            orderDate = datetime.datetime.strptime(orderData['children'][0]['orderInfo'][1]['content'], '%Y-%m-%d %H:%M')
            invalidDate = orderDate + datetime.timedelta(days=20)
            # 查询订单的改价记录
            print(self.account, '订单号码  ', orderId)
            inquireChangePriceStatusUrl = 'http://cs1.jakcom.it/Aliexpress_Promotion/changepricelog_byorderid'
            params = {'orderid': orderId}
            inquireChangePriceStatusResponse = requests.get(inquireChangePriceStatusUrl, params=params)
            changeRule = inquireChangePriceStatusResponse.json()['change_rule']
            changeTime = inquireChangePriceStatusResponse.json()['time']
            totalAmount, productAmount = self.getPayAmount(orderUrl)
            countdown = (invalidDate.date() - datetime.datetime.now().date()).days
            print(countdown)
            # '''
            # 获取订单的剩余时间, 订单总额, 商品价格
            print(self.account, '订单关闭倒计时 ', countdown)
            print(self.account, '修改时间  ', changeTime)
            print(productAmount)
            print(totalAmount)
            print(remark)
            # if productAmount >= totalAmount:
            #     continue
            checkDiscountCodeData = self.checkDiscountCode(remark)
            print(checkDiscountCodeData)
            # 若改价规则为 None   表明该订单第一次进行改价
            print(changeRule, changeTime)
            if changeRule is None:
                # 若checkDiscountCodeData 不为False  表明为 优惠码 改价
                if checkDiscountCodeData is not False:
                    print('优惠码改价')
                    discountRate, discountCode, discountDBId, discountValue = checkDiscountCodeData
                    discountData = {'discountCode': discountCode, 'discountDBId': discountDBId}
                    self.reductionPrice(orderId, discountRate, totalAmount, discountData, discountValue)
                # 若最后改价时间不是今天
                elif changeTime != str(datetime.datetime.now().date()):
                    print('绝对值改价1')
                    # 使用绝对值改价
                    discountRate = 1 - (20 - int(countdown)) * 0.02
                    self.reductionPrice(orderId, discountRate, totalAmount, countdown)
            elif changeTime != str(datetime.datetime.now().date()):
                print('绝对值改价2')
                discountRate = 1 - (20 - int(countdown)) * 0.02
                self.reductionPrice(orderId, discountRate, totalAmount, countdown)
            # '''

    # 检测优惠码是否可用
    def checkDiscountCode(self, remark):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/coupon_identitication'
        data = {
            'account': self.account,
            'desc': remark.upper(),
            # 'desc': (remark + ' 52KP').upper(),
        }
        response = requests.post(url, data=data).json()
        print(response)
        discountRate = response['Discount_Rate']
        discountCode = response['Coupon_Code']
        discountDBId = response['Sys_Id']
        discountValue = response['Discount_Value']
        expiredDate = response['Expired_Date']
        if discountCode is not None and discountDBId is not None and discountRate is not None:
            today = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(str(datetime.datetime.now()).split('.')[0], "%Y-%m-%d %H:%M:%S"))
            expiredDate = time.strftime("%Y/%m/%d %H:%M:%S", time.strptime(expiredDate.replace('/', '-'), "%Y-%m-%d %H:%M:%S"))
            if expiredDate > today:
                return discountRate, discountCode, discountDBId, discountValue
            else:
                return False
        else:
            return False

    # 降价
    def reductionPrice(self, orderId, discountRate, totalAmount, discountData, discountValue=0):
        url = 'https://trade.aliexpress.com/order/modifyOrder.json'
        if discountValue == 0:
            reductionPrice = (1 - float('%.2f' % float(discountRate))) * float(totalAmount)
            remind = 'Congratulations, you already successfully get a {:.0f}% off shopping opportunity today!'.format(float(discountRate) * 100)
        else:
            reductionPrice = discountValue
            remind = "Congratulations, you already successfully get a {:.0f}USD off shopping opportunity today!" .format(discountRate)
        # reductionPrice = (1 - float('%.2f' % float(discountRate))) * float(totalAmount) if discountValue == 0 else discountValue
        finalPrice = float(totalAmount) - float(reductionPrice)
        print(self.account, '原价  ', totalAmount)
        print(self.account, '降价  %f' % reductionPrice)
        print(self.account, '价格  %f' % finalPrice)
        print(self.account, '折扣率  %s' % discountRate)
        self.setCookie(orderId)
        csrfToken = self.getCsrfToken(orderId)
        # remind = 'Congratulations, you already successfully get a {:.0f}% off shopping opportunity today!'.format(float(discountRate) * 100) if discountValue == 0 else "Congratulations, you already successfully get a {:.0f}USD off shopping opportunity today!" .format(float(discountRate) * 100)
        data = {
            'orderId': orderId,
            # 'sellerDiscount': -1,
            'sellerDiscount': float('-%.2f' % reductionPrice),
            'sellerDiscountText': remind,
            'orderFrom': 'N',
            'rnd': 0.199553014582043,
            '_csrf_token': csrfToken,
            'csrf_token': csrfToken
        }
        logData = {
            'account': self.account,
            'orderid': orderId,
            'original_price': totalAmount,
            'current_price': finalPrice,
            'change_rule': '优惠码' if isinstance(discountData, dict) else '订单关闭倒计时',
            'remark': '%s - %s' % (discountData['discountCode'], discountData['discountDBId']) if isinstance(
                discountData, dict) else '产品原价 %s, 距离关闭还有 %s天，折扣率为 %s, 优惠金额 %s' % (totalAmount, discountData, discountRate, reductionPrice),
            'time': str(datetime.datetime.now().date())
        }
        # print(logData)
        print(data)
        headers = {
            'authority': 'trade.aliexpress.com',
            'method': 'POST',
            'path': '/order/modifyOrder.json',
            'scheme': 'https',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'content-length': '255',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': self.cookie,
            'origin': 'https://trade.aliexpress.com',
            'referer': 'https://trade.aliexpress.com/order_detail.htm?orderId={}&discount_list=true'.format(orderId),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = requests.post(url, headers=headers, data=data)
        print(response)
        print(response.reason)
        print(response.text)
        print(self.cookie)
        status = response.json()['content']['success']
        if status is True:
            print(logData)
            self.log(logData)

    # 日志
    def log(self, data):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/changeprice_logger'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self):
        # pass
        self.getOrderId()
        # self.checkDiscountCode('')


# 获取速卖通全部账号
def get_account():
    url = 'http://py2.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def sendMail(account):
    changePrice = ChangePrice(account)
    changePrice.main()
    # try:
    #     changePrice.orderPayCountdownSelenium.quit()
    # except:
    #     pass


def send_test_log(logType, msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.160:90/Log/Write'
    data = {
        'LogName': '速卖通改价',
        'LogType': logType,
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)


def main():
    accountList = get_account()
    # sendMail('fb2@jakcom.com')
    # while True:
    #     for account in accountList:
    #         try:
    #             sendMail(account)
    #         except Exception as e:
    #             pass

    for account in accountList:
        while True:
            time.sleep(1)
            threading.Thread(target=sendMail, args=(account)).start()
        # print('**' * 50 )
        # print(account)
        # sendMail(account)
        # print('**' * 50 )
        # time.sleep(3)


if __name__ == '__main__':
    main()
