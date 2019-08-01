# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: newPassengerTreasure_selenium.py.py
@time: 2019/5/16 11:01
@desc: 新客宝 每日一次 01:00以后
@updateTime: 2019/6/19 13:03
@UpdateDetails: 将原来的selenium任务更改为API接口任务
"""
import re
import json
import datetime
import requests
from DynamicAnnouncement.public import Public


class NewPassengerTreasure(Public):
    def __init__(self):
        super(NewPassengerTreasure, self).__init__()
        self.csrf_token = self.get_csrf_token()
        # 获取全部商品价格
        self.price_dict = self.get_product_price()
        # 获取产品优惠等级
        self.activity_level = self.get_activity_lev()

    # 获取csrf_token
    def get_csrf_token(self):
        url = 'https://widget.1688.com/front/ajax/bridge.html'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r'__mbox_csrf_token=(.*?);', re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.headers['Set-Cookie'])[0]
        self.cookie = self.cookie + '__mbox_csrf_token=%s' % csrf_token
        self.headers['cookie'] = self.cookie
        return csrf_token

    # 获取产品优惠等级
    def get_activity_lev(self):
        print('正在获取产品优惠等级')
        # 获取昨天新发商品链接
        url = 'http://192.168.1.190:5000/1688/get/products/yesterday'
        response = requests.get(url)
        datas = eval(response.text)
        activity_level = {
            'A': {'level': 5, 'product': []},
            'B': {'level': 10, 'product': []},
            'C': {'level': 20, 'product': []},
        }
        for data in datas:
            # 若sku 为N2 则修改为 N2X
            sku = data[0] if data[0] != 'N2' else 'N2X'
            name = data[1]
            id = data[2]
            product_dict = {
                'sku': sku,
                'name': name,
                'id': id
            }
            if self.price_dict[sku] <= 50:
                activity_level['A']['product'].append(product_dict)
            elif self.price_dict[sku] > 50 and self.price_dict[sku] <= 100:
                activity_level['B']['product'].append(product_dict)
            else:
                activity_level['C']['product'].append(product_dict)
        return activity_level

    # 获取商品价格
    def get_product_price(self):
        # 商品价格目标链接
        print('正在获取商品价格')
        url = 'http://192.168.1.160:90/alibaba/Get_prices'
        response = requests.get(url)
        datas = json.loads(response.text)
        price_dict = {data['sku']: data['dropship_cn_rmb'] for data in datas}
        return price_dict

    # 首页
    def index(self, level, data):
        url = 'https://widget.1688.com/front/ajax/getJsonComponent.json'
        # 这月
        date_month = datetime.datetime.now().month
        # 今天
        date_day = datetime.datetime.now().day
        # 如果月份为1位数，将月份补位2位
        date_month = str(date_month).zfill(2)
        date_day = str(date_day).zfill(2)
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=30)
        # 活动名称
        title = '新人专享_{}'.format(str(date_month) + str(date_day) + level)
        post_data = {
            'namespace': 'saveMarketingTopic',
            'widgetId': 'saveMarketingTopic',
            'methodName': 'execute',
            'params': json.dumps({
                "promotionCode": "myh_price_nocondition",
                "promotionName": "满优惠",
                "marketingScene": "myh",
                 "hasAmountAt": True,
                "hasCountAt": False,
                "hasDiscountRate": False,
                "hasDecreaseMoney": True,
                "amountAt": '%s.01' % data['level'],
                "decreaseMoney": data['level'],
                "status": "EDITING",
                "marketingTopicId": None,
                "name": title,
                "templateCode": "newbuyer",
                "templateName": "新客宝",
                "startTime": "%s 00:00:00" % start_date,
                "endTime": "%s 00:00:00" % end_date,
                "allShopParticipate": False,
                "isPartMember": False,
                "isShopNewBuyer": True,
                "purchaseLevel1": [],
                "purchaseLevel2": [],
                "purchaseLevel3": [],
                "excludeAreas": []
            }),
            '__mbox_csrf_token': self.csrf_token,
        }
        self.headers['orinig'] = 'https://widget.1688.com'
        self.headers['referer'] = 'https://widget.1688.com/front/ajax/bridge.html?target=brg-03547'
        self.headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        response = requests.post(url ,data=post_data, headers=self.headers)
        activityId = response.json()['content']['data']['id']
        status = self.add_products(activityId, data)
        if status:
            self.log(createTime=start_date, activityName=title, cutoffTime=end_date)
            self.send_test_log(logName='新客宝', logType='Run', msg='{} 发布成功'.format(title))

    # 添加商品
    def add_products(self, activityId, productDatas):
        url = 'https://widget.1688.com/front/ajax/getJsonComponent.json'
        promotions = []
        for productData in productDatas['product']:
            product = {
                "offerId":int(productData['id']),
                "discountRate":None,
                "fixPrice":None,
                "limitCount":None
            }
            promotions.append(product)
        data = {
            'namespace': 'saveActivityDetails',
            'widgetId': 'saveActivityDetails',
            'methodName': 'execute',
            'params': json.dumps({"id":str(activityId),"promotions":promotions}),
            'id': '40834114',
            'promotions': json.dumps(promotions),
            '__mbox_csrf_token': self.csrf_token,
        }
        try:
            response = requests.post(url, data=data, headers=self.headers)
            print(response.text)
            status = response.json()['hasError']
            if status is False:
                return True
            else:
                self.send_test_log(logName='新客宝', logType='Error', msg='{} 发布成功'.format(response.json()))
        except Exception as e:
            self.send_test_log(logName='新客宝', logType='Error', msg='{} 发布成功'.format(str(e)))

    def log(self, createTime, activityName, cutoffTime):
        url = 'http://192.168.1.160:90/OSEE/xinkelog'
        data = {
            'Account': 'jakcomcom',
            'Createtime': createTime,
            'activityname': activityName,
            'cutofftime': cutoffTime
        }
        response = requests.post(url, data=data)
        print(response.text)

    def main(self):
        # pass
        # 便利每种优惠等级
        for level, data in self.activity_level.items():
            # self.index(level, data)
            try:
                self.index(level, data)
            except Exception as e:
                self.send_test_log(logName='新客宝', logType='Error',
                                   msg='{} {} 发布失败 {}'.format(datetime.datetime.now().date(), level, str(e)))
                continue


def main():
    newPassengerTreasure = NewPassengerTreasure()
    newPassengerTreasure.main()


if __name__ == '__main__':
    main()