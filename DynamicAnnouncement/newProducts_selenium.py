# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: newProducts_selenium.py
@time: 2019/5/16 22:11
@desc: 新品推荐 每日01:00运行,一天一次
"""
import re
import json
import time
import requests
import datetime
from DynamicAnnouncement.public_selenium import Public_selenium


class NewProducts(Public_selenium):

    # 类的初始化
    def __init__(self):
        # 继承父类Public_selenium 的init方法
        super(NewProducts, self).__init__('https://work.1688.com/home/page/index.htm?_path_=sellerBaseNew/2017sellerbase_yingxiao/newproduct')
        # 记录每天推荐的个数
        self.product_number = 0
        # 获取每天的新品数量、访客数量、支付买家数、支付商品数、动销率
        self.new_numbers, self.uv, self.payBuyerCount, self.payItemQuantity, self.dealRate = self.getNewOfferShopStatisticData()

    # 首页
    def index(self):
        time.sleep(2)
        # 获取总页数
        page_number = self.browser.find_element_by_xpath('//*[@class="next-pagination-display"]').text.split('/')[1]
        for page in range(int(page_number)):
            print('正在推荐商品，共{}页，当前第{}页'.format(page_number, page))
            try:
                # 点击全选框
                self.browser.find_element_by_xpath('//*[@class="next-table-header-node first next-table-selection"]/div/label/input').click()
                time.sleep(1)
                # 点击设为推荐新品
                self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-normal next-btn-medium mr8 btn"]').click()
                time.sleep(1)
                # 点击下一页
                self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-normal next-btn-medium next-pagination-item next"]').click()
                # 获取每页的产品数量
                product_elements = self.browser.find_elements_by_xpath('//*[@class="next-table-row"]')
                product_number = len(product_elements) + 2
                self.product_number += product_number
                time.sleep(2)
            except Exception as e:
                print(e)
                self.send_test_log(logName='新品推荐', logType='Error', msg=str(e))
                continue
        self.log()

    # 获取每天的新品数量、访客数量、支付买家数、支付商品数、动销率
    def getNewOfferShopStatisticData(self):
        print('正在获取每天的新品数量、访客数量、支付买家数、支付商品数、动销率')
        # 获取数据的目标链接
        url = 'https://widget.1688.com/front/getJsonComponent.json'
        # 构造参数
        params = {
            'callback':'jQuery18305221836178973749_{}'.format(str(time.time()).replace('.', '')[:13]),
            'namespace': 'getNewOfferShopStatisticData',
            'widgetId': 'getNewOfferShopStatisticData',
            'methodName': 'execute',
            '_':str(time.time()).replace('.', '')[:13]
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        # 构造获取数据的正则表达式
        data_re_compile = re.compile(r'\((.*?)\)', re.S)
        data = re.findall(data_re_compile, response.text)[0]
        # 将数据转为json
        data = json.loads(data)['content']['newOfferShopStatisticData']
        # 新品数量
        new_numbers = data['newOfferCount']
        # 访客数
        uv = data['uv']
        # 支付买家数
        payBuyerCount = data['payBuyerCount']
        # 支付商品件数
        payItemQuantity = data['payItemQuantity']
        # 动销率
        dealRate = data['dealRate']
        return new_numbers, uv, payBuyerCount, payItemQuantity, dealRate

    def log(self):
        url = 'http://192.168.1.99:90/OSEE/Recommendproductlog'
        data = {
            'Account': 'jakcomcom',
            'Createtime': str(datetime.datetime.now()),
            'newcount': self.new_numbers,
            'visitornum': self.uv,
            'pay_clientnum': self.payBuyerCount,
            'pay_prouductnum': self.payItemQuantity,
            'market_rate': self.dealRate,
            'recommend_num': self.product_number
        }
        print(data)
        response = requests.post(url, data=data)
        print(response.text)


if __name__ == '__main__':
    newProducts = NewProducts()
    newProducts.index()
    newProducts.quit()