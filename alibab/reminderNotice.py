# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: reminderNotice.py
@time: 2019/6/22 11:54
@desc: 催付通知
"""
import sys
import time
import datetime
import requests
import threading
from alibaba.public import Public



class ReminderNotice(Public):
    def __init__(self, account):
        self.account = account
        super(ReminderNotice, self).__init__(self.account)
        self.ctoken = self.get_ctoken()

    # 获取订单付款链接
    def getOrderPayLink(self, orderId):
        url = 'https://sao.alibaba.com/invoke/trade/view_payment_link.json?'
        params = {
            'id': int(orderId),
            'payStep': 'FULL',
            'role': 'seller',
            'method': 'click',
            '_tb_token_': self.tb_token,
            'ctoken': self.ctoken,
        }
        headers = self.headers
        headers[
            'referer'] = 'https://biz.alibaba.com/ta/detail.htm?orderId=%s&tenant=TRADE&action=view_payment_link&listQuery=true&tracelog=from_orderlist_dropdown' % int(
            orderId)
        headers['origin'] = 'https://biz.alibaba.com'
        response = requests.get(url, params=params, headers=headers)
        paymentUrl = response.json()['data']['paymentUrl']
        return paymentUrl

    # 发送系统邮件
    def sendSystemNotice(self, data):
        url = 'https://sao.alibaba.com/invoke/trade/view_payment_link.json'
        orderId = data['orderId']
        title = ','.join([i['name'] for i in eval(data['product_datas'])])
        params = {
            'id': orderId,
            'tradeId': orderId,
            'role': 'seller',
            'payStep': 'FULL',
            '_tb_token_': self.tb_token,
            '_csrf_token_': '',
            'ctoken': self.ctoken,
        }
        headers = self.headers
        headers[
            'referer'] = 'https://biz.alibaba.com/ta/detail.htm?orderId=%s&tenant=TRADE&action=view_payment_link&listQuery=true&tracelog=from_orderlist_dropdown' % int(
            orderId)
        headers['origin'] = 'https://biz.alibaba.com'
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            logData = {
                'account': self.account,
                'channel': '系统邮件',
                'orderid': orderId,
                'title': title,
                'totalamount': data['initialPayment']
            }
            sendLog(logData)

    # 获取可催付的订单
    def getWaitPayOrder(self, sevenDaysDict=[], oneMonthDict=[]):
        url = 'http://cs1.jakcom.it/AlibabaOrderManage/get_ordermsg_waitpay?account=%s' % (self.account)
        response = requests.get(url)
        datas = response.json()
        if len(datas) == 0:
            return sevenDaysDict, oneMonthDict
        for index, data in enumerate(datas):
            buyerEmail = data['buyerEmail']
            buyerName = data['buyerName']
            buyerLoginId = data['buyerLoginId']
            buyerAddress = data['address']
            orderId = data['orderId']
            productData = data['product_datas']
            initialPayment = data['initialPayment']
            createDate = data['createdDate'].split()[0]
            today = datetime.datetime.now()
            sevenDaysAgo = str((today - datetime.timedelta(days=7)).date())
            oneMonthAgo = str((today - datetime.timedelta(days=30)).date())
            sendData = {
                'account': self.account,
                'buyerEmail': buyerEmail,
                'buyerName': buyerName,
                'buyerLoginId': buyerLoginId,
                'buyerAddress': buyerAddress,
                'orderId': orderId,
                'productData': productData,
                'initialPayment': initialPayment
            }
            # self.sendSystemNotice(data)
            try:
                self.sendSystemNotice(data)
            except Exception as e:
                send_test_log(logName='催付通知 系统邮件', logType='Error', msg=str(e))
            if '***' in buyerEmail or buyerLoginId is None or buyerAddress == '-':
                continue
            try:
                if createDate > sevenDaysAgo:
                    paymentUrl = self.getOrderPayLink(orderId)
                    sendData['paymentUrl'] = paymentUrl
                    sevenDaysDict.append(sendData)
                elif createDate > oneMonthAgo:
                    paymentUrl = self.getOrderPayLink(orderId)
                    sendData['paymentUrl'] = paymentUrl
                    oneMonthDict.append(sendData)
            except Exception as e:
                print(e)
        return sevenDaysDict, oneMonthDict

    # 主函数
    def main(self):
        sevenDaysDict, oneMonthDict = self.getWaitPayOrder()
        return sevenDaysDict, oneMonthDict


# 发送手动邮件催付
def sendEmailNotice(datas):
    for data in datas:
        inquireUrl = 'http://cs1.jakcom.it/AlibabaORDERmANAGE/get_calllog_byorderid'
        params = {
            'account': data['account'],
            'orderid': data['orderId'],
            'channel': '手动邮件'
        }
        print('**' * 50)
        print(data)
        print('**' * 50)
        inquireResponse = requests.get(inquireUrl, params=params)
        if int(inquireResponse.text) != 0:
            continue
        time.sleep(60)
        try:
            title = ','.join([i['name'] for i in eval(data['productData'])])
            productData = eval(str(data['productData']))
            productStr = ''
            for index, product in enumerate(productData):
                productHtml = """<tr>
                            <td>%s</td>
                            <td>
                                <img src="%s" alt="" width="50px" height="50px">
                                <a href="%s">%s</a>
                            </td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                        </tr>""" % (
                    index + 1, 'https:' + product['img'], 'https:' + product.get('link', ''), product['name'],
                    product['quantity'], product['unit'], product['currentUnitPrice'], product['currentProductPrice']
                )
                productStr += productHtml
            paymentUrl = data['paymentUrl']
            buyerAddress = data['buyerAddress']
            initialPayment = data['initialPayment']
            buyerName = data['buyerName'] if '???' not in data['buyerName'] else buyerAddress.split(',')[0]
            buyerName = 'Friend' if buyerName.isdigit() else buyerName
            html = '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Order Infomations</title>
            </head>
            <body>
            <table>
                <thead>
                <tr>
                    <td><b>Dear</b></td>
                    <td><b>{0} :</b></td>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <td></td>
                    <td><br>Thanks for your order;</td>
                </tr>
                <tr>
                    <td></td>
                    <td>Please confirm this below info;</td>
                </tr>
                <tr>
                    <td></td>
                    <td>If the order information is correct, please finish the payment within 24 hours, so that we can arrange your
                        goods in time;
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td>Thank you again for your support and trust.</td>
                </tr>
                <tr>
                    <td></td>
                    <td>
                        <br>
                        <b>Order detail link: </b><br>
                        <a href="{1}" target="_blank">{2}</a>
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td>
                        <b>Delivery address info: </b><br>
                        {3}
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td>
                        <br>
                        <table border="1" cellspacing="0" cellpadding="10">
                            <caption><b>Products info</b></caption>
                            <thead>
                            <tr bgcolor="#d3d3d3">
                                <th>Serial number</th>
                                <th>Product name</th>
                                <th>Quantity</th>
                                <th>Unit</th>
                                <th>Unit price</th>
                                <th>Total prices</th>
                            </tr>
                            </thead>
                            <tbody>
                            {4}
                            </tbody>
                            <tfoot>
                            <tr>
                                <td align="right" colspan="6">Total prices:{5}</td>
                            </tr>
                            </tfoot>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td>
                        <br>
                        Best regards<br>
                        Ady. Jakcom<br>
                        <br>
                        *************************************************<br>
                        <br>
                        Shanxi Jakcom Technology Co.,Ltd<br>
                        Tel: +86-18503462689<br>
                        Whatsapp: +86-18503462689<br>
                        Skype: jakcom2013<br>
                        QQ: 2145358518<br>
                        Wechat: 18503462689<br>
                        Other Information of Our Products:
                        <a href="http://b2b.JAKCOM.com" target="_blank"> http://b2b.JAKCOM.com</a>
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td>
                        <br>
                        <img src="http://www.jakcom.com/app/email/email_sign_picture.jpg" alt="" height="73%">
                    </td>
                </tr>
                </tbody>
            </table>
            </body>
            </html>
            '''.format(buyerName, paymentUrl, paymentUrl, buyerAddress, productStr, initialPayment)
            url = 'http://py1.jakcom.it:5000/tools_sms/post/email/alibaba_urge_pay'
            postData = {
                # 'to_add': 'wh.chnb@gmail.com',
                'to_add': data['buyerEmail'],
                'buyer_name': buyerName,
                'account': data['account'],
                'order_id': data['orderId'],
                'html_text': html
            }
            response = requests.post(url, postData)
            if response.status_code == 200:
                logData = {
                    'account': data['account'],
                    'channel': '手动邮件',
                    'orderid': data['orderId'],
                    'title': title,
                    'totalamount': float(data['initialPayment'].split('$')[1])
                }
                sendLog(logData)
            else:
                raise Exception('手动邮件 %s %s' % (data, response.status_code))
        except Exception as e:
            send_test_log(logName='催付通知 手动邮件', logType='Error', msg=str(e))


# 发送千牛
def sendQianNiuNotice(datas):
    for data in datas:
        try:
            url = 'http://py1.jakcom.it:5000/alibaba/post/sms/qianniu_urge_pay'
            title = ','.join([i['name'] for i in eval(data['productData'])])
            postData = {
                'account': data['account'],
                'buyer_id': data['buyerLoginId'],
                'buyer_name': data['buyerName'],
                'pay_link': data['paymentUrl'],
                'address_info': data['buyerAddress'],
                'orderid': data['orderId'],
                'title': title,
                'totalamount': float(data['initialPayment'].split('$')[1])
            }
            response = requests.post(url, postData)
            if response.status_code == 200:
                pass
                # logData = {
                #     'account': data['account'],
                #     'channel': '千牛',
                #     'orderid': data['orderId'],
                #     'title': title,
                #     'totalamount': data['initialPayment']
                # }
                # sendLog(logData)
            else:
                raise Exception('千牛 %s %s' % (data, response.status_code))
        except Exception as e:
            send_test_log(logName='催付通知 千牛催付', logType='Error', msg=str(e))


# 日志
def sendLog(data):
    url = 'http://cs1.jakcom.it/AlibabaOrderManage/ordercalllog_save'
    response = requests.post(url, data=data)
    print(response)
    print(response.text)


def send_test_log(logName, logType, msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.160:90/Log/Write'
    data = {
        'LogName': logName,
        'LogType': logType,
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)


def main():
    sevenDaysDict, oneMonthDict = [], []
    accountList = [
        # 'fb1@jakcom.com',
        # 'fb2@jakcom.com',
        'fb3@jakcom.com',
        # 'tx@jakcom.com',
    ]
    for account in accountList:
        reminderNotice = ReminderNotice(account)
        accountSevenDaysDict, accountOneMonthDict = reminderNotice.main()
        sevenDaysDict.extend(accountSevenDaysDict)
        oneMonthDict.extend(accountOneMonthDict)
    print(oneMonthDict)
    qianNiu = threading.Thread(target=sendQianNiuNotice, args=(sevenDaysDict,))
    qianNiu.start()
    email = threading.Thread(target=sendEmailNotice, args=(oneMonthDict,))
    email.start()


if __name__ == '__main__':
    main()
