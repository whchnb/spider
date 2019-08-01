# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: marketPlan.py
@time: 2019/7/18 10:03
@desc:  营销计划
"""
import time
import json
import datetime
import requests
import xmltodict
from aliexpressNew.public import Public


class MarketPlan(Public):
    def __init__(self, account):
        self.account = account
        super(MarketPlan, self).__init__(self.account)
        self.csrfToken = self.get_csrf_token()

    # 获取添加的商品
    def addProducts(self):
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/getproducts_hotsale?account=' + self.account
        response = requests.get(url)
        productIdList = [i['Product_ID'] for i in response.json()]
        return productIdList

    # 获取正在计划中的商品
    def onlineProducts(self):
        url = 'https://afseller.aliexpress.com/affiliate/productCommission/listProductCommission.do'
        params = {
            'isHot': True,
            'pageSize': '50',
            'validIndex': '1',
            'invalidIndex': '1',
        }
        response = requests.get(url, headers=self.headers, params=params)
        xmlparse = xmltodict.parse(response.text)
        jsonstr = json.dumps(xmlparse, indent=1)
        datas = json.loads(jsonstr)['ResponseResult']['data']
        foreverProductDatas = datas.get('afSellerPromotionProduct', []) if isinstance(datas.get('afSellerPromotionProduct', []), list) else [datas['afSellerPromotionProduct']]
        expiredProductDatas = datas.get('expiringAfSellerPromotionProduct', []) if isinstance(datas.get('expiringAfSellerPromotionProduct', []), list) else [datas['expiringAfSellerPromotionProduct']]
        foreverProductIdList = [i['productId'] for i in foreverProductDatas]
        expiredProductIdList = [i['productId'] for i in expiredProductDatas]
        return foreverProductIdList, expiredProductIdList

    # 查找商品详细信息
    def inquireProduct(self, productId):
        url = 'https://afseller.aliexpress.com/affiliate/productCommission/listProductDetailInfo.do'
        params = {
            'isHot': True,
            'searchText': productId,
            'productGroup': '',
            'pageNo': '1',
        }
        response = requests.get(url, headers=self.headers, params=params)
        xmlparse = xmltodict.parse(response.text)
        jsonstr = json.dumps(xmlparse, indent=1)
        data = json.loads(jsonstr)['ResponseResult']['data']['productCommissions']
        data['maxRate'] = 90
        data['minRate'] = 5
        data['rate'] = 8
        data['setRate'] = 8
        data['setValidDate'] = str((datetime.datetime.now() + datetime.timedelta(hours=-12)).date())
        data['exists'] = False
        data['offline'] = False
        data['smart'] = False
        data['visible'] = True
        data['leafCategoryId'] = int(data['leafCategoryId'])
        data['productId'] = int(data['productId'])
        data['rootCategoryId'] = int(data['rootCategoryId'])
        data['secondCategoryId'] = int(data['secondCategoryId'])
        return data

    # 需要添加的商品
    def needAddProducts(self, needAddProductIdSet):
        productDataList = []
        for productId in list(needAddProductIdSet):
            productData = self.inquireProduct(productId)
            productDataList.append(productData)
        url = 'https://afseller.aliexpress.com/affiliate/productCommission/addProductCommissions.do'
        data = {
            'isHot': True,
            'productCommissions': json.dumps(productDataList)
        }
        headers = self.headers
        headers['x-xsrf-token'] = self.csrfToken
        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=headers, data=data)
        try:
            xmlparse = xmltodict.parse(response.text)
            jsonstr = json.dumps(xmlparse, indent=1)
            datas = json.loads(jsonstr)
        except Exception as e:
            print(e)
            self.send_test_log(logName='营销计划', logType='Error', position='needAddProducts', msg=self.account + ',' + str(e))

    # 需要移除的商品
    def needDeleteProducts(self, needDeleteProductIdSet):
        for productId in needDeleteProductIdSet:
            url = 'https://afseller.aliexpress.com/affiliate/productCommission/removeProductCommission.do'
            data = {
                'isHot': True,
                'productId': productId
            }
            headers = self.headers
            headers['x-xsrf-token'] = self.csrfToken
            # headers['content-type'] = 'application/x-www-form-urlencoded'
            response = requests.post(url, headers=headers, data=data)
            try:
                xmlparse = xmltodict.parse(response.text)
                jsonstr = json.dumps(xmlparse, indent=1)
                datas = json.loads(jsonstr)
            except Exception as e:
                print(e)
                self.send_test_log(logName='营销计划', logType='Error', position='needDeleteProducts',msg=self.account + ',' + str(e))

    # 需要恢复的商品
    def needRecoverProducts(self, needRecoverProductIdSet):
        for productId in needRecoverProductIdSet:
            url = 'https://afseller.aliexpress.com/affiliate/productCommission/recoverProductCommission.do'
            data = {
                'isHot': True,
                'productId': productId
            }
            headers = self.headers
            headers['x-xsrf-token'] = self.get_csrf_token()
            response = requests.post(url, headers=self.headers, data=data)
            try:
                xmlparse = xmltodict.parse(response.text)
                jsonstr = json.dumps(xmlparse, indent=1)
                datas = json.loads(jsonstr)
            except Exception as e:
                print(e)
                self.send_test_log(logName='营销计划', logType='Error', position='needDeleteProducts',
                                   msg=self.account + ',' + str(e))

    def main(self):
        try:
            productIdList = self.addProducts()
            foreverProductIdList, expiredProductIdList = self.onlineProducts()
            onlineProductIds = foreverProductIdList + expiredProductIdList
            # 需要添加的商品
            needAddProductIdSet = set(productIdList).difference(set(onlineProductIds))
            # 需要移除的商品
            needDeleteProductIdSet = set(foreverProductIdList).difference(set(productIdList))
            # 需要恢复的商品
            needRecoverProductIdSet = set(expiredProductIdList).intersection(set(productIdList))
            print(needAddProductIdSet)
            if len(needAddProductIdSet) != 0:
                self.needAddProducts(needAddProductIdSet)
            print(needDeleteProductIdSet)
            if len(needDeleteProductIdSet) != 0:
                self.needDeleteProducts(needDeleteProductIdSet)
            print(needRecoverProductIdSet)
            if len(needRecoverProductIdSet) != 0:
                self.needRecoverProducts(needRecoverProductIdSet)

        except Exception as e:
            self.send_test_log(logName='营销计划', logType='Error', position='needDeleteProducts',
                               msg=self.account + ',' + str(e))


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
    for account in accountList[5:]:
        # account = 'fb2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        try:
            marketPlan = MarketPlan(account)
            marketPlan.main()
            time.sleep(3)
        except Exception as e:
            bug(logName='营销计划', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()
