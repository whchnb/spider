# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: fanMarket.py
@time: 2019/7/18 13:50
@desc: 粉丝营销
"""
import re
import time
import datetime
import requests
from aliexpressNew.public import Public


class FanMarket(Public):
    def __init__(self, account):
        self.account = account
        super(FanMarket, self).__init__(self.account)

    # 获取xsrftoken
    def getXsrfToken(self):
        xsrfToken = re.findall(re.compile(r'XSRF-TOKEN=(.*?);', re.S), self.cookie)[0]
        return xsrfToken

    # 获取店铺id
    def getStoreId(self):
        url = 'https://afseller.aliexpress.com/stat/dashboard.htm'
        response = requests.get(url, headers=self.headers)
        store_id_re_compile = re.compile(r'http://www.aliexpress.com/store/(\d*?)&', re.S)
        store_id = re.findall(store_id_re_compile, response.text)[0]
        return store_id

    # 获取要添加的产品
    def getProducts(self):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/get_visitor_newproducts?account=' + self.account
        response = requests.get(url)
        datas = response.json()
        productIdList = [i['Product_ID'] for i in datas]
        self.product_dict = {}
        for data in datas:
            product_id = data['Product_ID']
            self.product_dict[product_id] = {
                'Title': data['Title'],
                'Visitors': data['Visitors'],
                'SKU': data['SKU'],
            }
        return productIdList

    # 提交
    def submit(self):
        productIds = self.getProducts()
        xsrfToken = self.getXsrfToken()
        today = datetime.datetime.now().date()
        title = 'JAKCOM Technology 「{}」recommend products;\nBut only you can enjoy more discounts, please accept it;\nPlease feel free to message us if you have any questions;\nHave a good week.'.format(str(today).replace('-', ''))
        publishTime = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)), "%Y-%m-%d"))).replace('.', '') + '00'
        url = 'https://shopnews.aliexpress.com/fanszone/PublishNewArrivalsAjax.do'
        data = {
            'postId': '',
            'summary': title,
            'productIds': ','.join(productIds),
            'ruleId': '0',
            'delayPublishedTime': publishTime,
            'image': '',
            'cateId': '',
            'lang': 'zh_CN',
            'origin': '0',
            'themeid': '',
            'gameType': '',
            'gameInCode': '',
            'toSnsAccounts': '[]',
        }
        headers = self.headers
        headers['x-xsrf-token'] = xsrfToken
        response = requests.post(url, headers=headers, data=data)
        print(response)
        print(response.text)
        return response.json()['code']

    # 提交日志
    def sendLog(self):
        for product_id,product_data in self.product_dict.items():
            store_id = self.getStoreId()
            url = 'http://cs1.jakcom.it/Aliexpress_Promotion/fans_promotionlog'
            data = {
                'account': self.account,
                'type': '上新贴',
                'game': '无',
                'subject': product_data['Title'],
                'productid': product_id,
                'url': 'https://www.aliexpress.com/item/%s.html?storeId=%s' % (product_id, store_id),
                'visitors': product_data['Visitors'],
                'time': str(datetime.datetime.now().date())
            }
            response = requests.post(url, data=data)
            print(response.text)

    def main(self):
        try:
            code = self.submit()
            if code == 0:
                self.sendLog()
                self.send_test_log(logName='粉丝营销', logType='Run', msg='%s' % self.account)
            else:
                self.send_test_log(logName='粉丝营销', logType='Error', msg='%s' % self.account)
        except Exception as e:
            self.send_test_log(logName='粉丝营销', logType='Error', msg='%s %s' % (self.account, str(e)))


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
    for account in accountList[1:]:
        # account = 'fb2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            fanMarket = FanMarket(account)
            fanMarket.main()
            time.sleep(3)
        except Exception as e:
            bug(logName='粉丝营销', msg='%s %s' % (account, str(e)))



if __name__ == '__main__':
    main()