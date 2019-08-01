# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: singleProductDiscount.py
@time: 2019/7/17 12:42
@desc: 单品折扣活动
@detail: 速卖通限时限量折扣与全店铺打折活动合并
"""
import re
import time
import json
import datetime
import requests
from aliexpressNew.public import Public
from concurrent.futures import ThreadPoolExecutor


class SingleProductDiscount(Public):
    def __init__(self, account):
        self.account = account
        super(SingleProductDiscount, self).__init__(self.account)
        self.sellerId = self.getSellerId()
        self.productsIds = []

    # 获取买家ID
    def getSellerId(self):
        url = 'https://gsp.aliexpress.com/apps/promotion/index'
        response = requests.get(url, headers=self.headers)
        sellerId = re.findall(re.compile(r'"whiteListId":"(\d*?)"', re.S), response.text)
        return sellerId[0]

    # 创建活动时间,并返回活动id
    def createActivityDate(self):
        today = datetime.datetime.now().date()
        self.title = 'New Products Promotion {}'.format(str(today).replace('-', ''))
        # 构造开始时间
        today = datetime.datetime.now().date()
        self.startDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=1)) + ' 15:00:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        # 构造结束时间
        self.endDate = str(time.mktime(time.strptime(str(today + datetime.timedelta(days=31)) + ' 14:59:00', "%Y-%m-%d %H:%M:%S"))).split('.')[0] + '000'
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.single.save'
        data = {
            '_timezone': '-8',
            # 'spm': '5261.promotion_single_index.createPromotion.1.146f3e5fwLbFPy',
            'operation': 'add',
            'step': '0',
            'campaignId': '',
            'promotionName': self.title,
            'timeRange': '%s,%s' % (self.startDate, self.endDate),
        }
        response = requests.post(url ,data=data, headers=self.headers)
        promotionUrl = response.json()['data']['href']
        # promotionUrl = '/apps/promotion/single/products?promotionId=1726435674'
        return promotionUrl

    # 获取商品
    def getProducts(self):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/singleproduct_discount?account=' + self.account
        response = requests.get(url)
        productIds = eval(response.text)
        print(len(productIds))
        # productIds = [4000013375470, 4000013430343, 4000013424226, 4000012695103, 4000012714468]
        return productIds

    # 添加商品
    def addProducts(self, productId):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.product.manager.render.list'
        data = {
            'jsonBody': json.dumps(
                {
                    "filter": {
                        "queryGroup": None,
                        "queryCategory": None,
                        "queryOwner": None,
                        "queryRegionalPricing": None,
                        "queryStock": None,
                        "queryShippingTemplate": None,
                        "querySelectInput": {
                            "key": 1,
                            "value": productId
                        }
                    },
                    "pagination": {"current": 1, "pageSize": 10}, "table": {"sort": {}},
                    "tab": "online_product"
                }
            )
        }
        response =requests.post(url, headers=self.headers, data=data)
        # print(response.text)
        productData = json.loads(response.json()['data'])['table']['dataSource'][0]
        productDataDict ={
            'checked': True,
            'itemId': str(productData['productId']),
            'sellerId': self.sellerId,
            'price': 'US $' + productData['price']['subItems'][0]['text'],
            'name': {
                'image': productData['itemDesc']['img'],
                'detailPageUrl': productData['itemDesc']['desc'][1]['href'],
                'subTitle': productData['itemDesc']['desc'][1]['text'],
                'uiType': 'TableProductCell',
                'title': productData['itemDesc']['desc'][0]['text']
            },
            'remarks': [],
            'primaryKey': str(productData['productId'])
        }
        addProductUrl = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.single.product.add'
        addProductData = {
            '_timezone': '-8',
            'operation': 'edit',
            'promotionId': self.promotionId,
            'marketingToolCode': 'limitedDiscount',
            'maxSelection': '100',
            'disabled': False,
            'startTime': self.startDate,
            'endTime': self.endDate,
            'checked': productData['productId'],
            'unchecked': '',
            'table': [productDataDict]
        }
        addProductResponse = requests.post(addProductUrl, data=addProductData, headers=self.headers)
        print(addProductResponse.json())
        self.setDiscount(productData['productId'])
        self.setLimitBuy(productData['productId'])

    # 设置折扣
    def setDiscount(self, productIds, times=0):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.single.product.discount.post'
        data = {
            '_timezone': '-8',
            'operation': 'edit',
            'promotionId': self.promotionId,
            'primaryKey': productIds,
            'checked': productIds,
            'unchecked': '',
            'percentDiscount': '10',
            'extraDiscountType': '-1',
            'marketingToolCode': 'limitedDiscount',
            'maxSelection': '100',
            'disabled': False,
            'startTime': self.startDate,
            'endTime': self.endDate,
        }
        times += 1
        if times >= 3:
            pass
        try:
            response = requests.post(url, headers=self.headers, data=data)
            print(response.json())
        except:
            return self.setDiscount(productIds, times)

    # 设置限购
    def setLimitBuy(self,productIds, times=0):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.single.product.limitbuy.post'
        data = {
            '_timezone': '-8',
            'spm': '5261.promotion_single_index.Table.2.4b603e5fQ3498u',
            'operation': 'edit',
            'promotionId': self.promotionId,
            'primaryKey': productIds,
            'checked': productIds,
            'unchecked': '',
            'limitBuyPerCustomer': '5',
            'marketingToolCode': 'limitedDiscount',
            'maxSelection': '100',
            'disabled': False,
            'startTime': self.startDate,
            'endTime': self.endDate,
        }
        times += 1
        if times >= 3:
            pass
        try:
            response = requests.post(url, headers=self.headers, data=data)
            print(response.json())
            self.productsIds.append(str(productIds))
        except:
            return self.setLimitBuy(productIds, times)

    # 保存活动
    def saveActivity(self, times=0):
        url = 'https://gsp-gw.aliexpress.com/openapi/param2/1/gateway.seller/api.promotion.single.status.update'
        data = {
            '_timezone': '-8',
            'spm': '5261.promotion_single_index.Table.2.4b603e5fQ3498u',
            'operation': 'edit',
            'promotionId': self.promotionId,
            'promotionType': 'limitedDiscount',
            'sellerId': self.sellerId,
            'refer': 'productManagePage',
            'successRedirectLink': '/apps/promotion/single/index',
            'operatorId': self.sellerId,
            'status': 'ongoing',
            'step': '1',
            'tableContainer': [],
        }
        times += 1
        if times >= 3:
            print('设置失败')
            self.send_test_log(logName='单品折扣', logType='Error', msg='{} 自建活动创建失败'.format(self.account))
            return
            pass
        try:
            response = requests.post(url, headers=self.headers, data=data)
            print(response.json())
            if response.json()['success'] is True:
                self.send_test_log(logName='单品折扣', logType='Run',msg='{} 自建活动 创建成功'.format(self.account))
                log_data = {
                    'Account': self.account,
                    'Promotion_type': '单品折扣',
                    'Channel': '自建活动',
                    'Promotion_Name': self.title,
                    'Begin_time': str(datetime.datetime.now().date() + datetime.timedelta(days=1)) + ' 15:00:00',
                    'End_time': str(datetime.datetime.now().date() + datetime.timedelta(days=31)) + ' 14:59:00',
                    'ProductID': ','.join(self.productsIds),
                }
                self.log(log_data)
        except Exception as e:
            print(e)
            return self.saveActivity(times)

    def main(self):
        # productIds = self.getProducts()
        promotionUrl = self.createActivityDate()
        self.promotionId = promotionUrl.split('=')[-1]
        print(promotionUrl)
        productIds = self.getProducts()
        pool = ThreadPoolExecutor(40)
        for index, productId in enumerate(productIds):
            print(index)
            try:
                pool.submit(self.addProducts, (productId))
            except Exception as e:
                print('ERROR ' + str(index) + str(e))
        pool.shutdown(wait=True)
        self.saveActivity()


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
        account = 'leliu2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            start = time.time()
            singleProductDiscount = SingleProductDiscount(account)
            singleProductDiscount.main()
            print(time.time() - start)
            time.sleep(3)
        except Exception as e:
            bug(logName='单品折扣', msg='{} 自建活动创建失败 {}'.format(account, str(e)))

if __name__ == '__main__':
    main()
