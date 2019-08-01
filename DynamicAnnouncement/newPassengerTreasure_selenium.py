# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: newPassengerTreasure_selenium.py.py
@time: 2019/5/16 11:01
@desc: 新客宝 每日一次 01:00以后
"""
import time
import json
import datetime
import requests
from selenium.webdriver.common.keys import Keys
from DynamicAnnouncement.public_selenium import Public_selenium


class NewPassengerTreasure(Public_selenium):

    # 类的初始化
    def __init__(self):
        # 继承父类init 方法
        super(NewPassengerTreasure, self).__init__(
            'https://work.1688.com/home/page/index.htm?&_path_=sellerBaseNew/2017sellerbase_yingxiao/seller_activitycreator')
        # 获取全部商品价格
        self.price_dict = self.get_product_price()
        # 获取产品优惠等级
        self.activity_level = self.get_activity_lev()

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

    # 运行入口
    def main(self):
        # 便利每种优惠等级
        for level, data in self.activity_level.items():
            # self.index(level, data)
            try:
                self.index(level, data)
            except Exception as e:
                self.send_test_log(logName='新客宝', logType='Error', msg='{} {} 发布失败 {}'.format(datetime.datetime.now().date(), level, str(e)))
                continue

    # 首页
    def index(self, level, data):
        # 选择新客宝，点击下一步
        self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-primary next-btn-medium"]').click()
        time.sleep(1)
        # 今年
        date_year = datetime.datetime.now().year
        # 这月
        date_month = datetime.datetime.now().month
        # 今天
        date_day = datetime.datetime.now().day
        # 如果月份为1位数，将月份补位2位
        date_month = str(date_month).zfill(2)
        date_day = str(date_day).zfill(2)
        # 活动名称
        title = '新人专享_{}'.format(str(date_month) + str(date_day) + level)
        # 全选活动名称
        self.browser.find_element_by_xpath('//*[@id="activityName"]').send_keys(Keys.CONTROL + 'a')
        # 删除
        self.browser.find_element_by_xpath('//*[@id="activityName"]').send_keys(Keys.DELETE)
        # 写入活动名称
        self.browser.find_element_by_xpath('//*[@id="activityName"]').send_keys(title)
        # 构造活动开始时间
        start_date = str(date_year) + str(date_month) + str(date_day)
        # 构造活动结束时间
        end_date = str(date_year) + str(int(date_month) + 1).zfill(2) + str(date_day)
        # 点击时间框
        self.browser.find_element_by_xpath('//*[@class="next-range-picker-trigger"]').click()
        # 获取活动时间开始元素
        start_date_element = self.browser.find_element_by_xpath('//*[@class="next-range-picker-input"]/span[1]/input')
        # 全选
        start_date_element.send_keys(Keys.CONTROL + 'a')
        # 删除
        start_date_element.send_keys(Keys.DELETE)
        # 写入活动时间
        start_date_element.send_keys(start_date)
        end_date_element = self.browser.find_element_by_xpath('//*[@class="next-range-picker-input"]/span[4]/input')
        end_date_element.send_keys(Keys.CONTROL + 'a')
        end_date_element.send_keys(Keys.DELETE)
        end_date_element.send_keys(end_date)
        # 点击确定活动起始时间
        self.browser.find_element_by_xpath(
            '//*[@class="next-btn next-btn-primary next-btn-small next-date-picker-quick-tool-ok"]').click()
        # 输入优惠金额
        self.browser.find_element_by_xpath(
            '//*[@class="next-input next-input-single next-input-small inputText"]/input').send_keys(data['level'])
        # 点击下一步
        self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-primary next-btn-medium"]').click()
        time.sleep(3)
        # 点击全选框
        self.browser.find_element_by_xpath(
            '//*[@id="__hex__"]/div/div/div[2]/div[4]/div/div/div/div/div[2]/div[6]/div[3]/div/div/div[1]/div/table/tbody/tr/th[1]/div/label/input').click()
        # 点击批量删除默认商品
        self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-normal next-btn-medium batch-btn"]').click()
        # 选择修改活动商品
        self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-secondary next-btn-medium"]').click()
        # 获取搜索框元素
        search_element = self.browser.find_element_by_xpath(
            '//*[@class="next-input next-input-single next-input-medium input"]/input')
        # 便利每个商品
        for product in data['product']:
            # print(product)
            try:
                # 全选
                search_element.send_keys(Keys.CONTROL + 'a')
                # 删除
                search_element.send_keys(Keys.DELETE)
                # 输入搜索名称
                search_element.send_keys(product['name'])
                # 点击搜索
                self.browser.find_element_by_xpath('//*[@class="search-area"]/button').click()
                time.sleep(1)
                # 选择添加
                self.browser.find_element_by_xpath('//*[@class="select-action undefined"]').click()
            except Exception as e:
                self.send_test_log(logName='新客宝', logType='Error', msg='可能是未查询到商品 {}'.format(str(e)))
        # 点击确认添加
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@class="btn-box"]/button[1]').click()
        time.sleep(1)
        # 完成并推广
        self.browser.find_element_by_xpath(
            '//*[@class="next-btn next-btn-primary next-btn-medium step-action"]').click()
        time.sleep(1)
        msg = self.browser.find_element_by_xpath('//*[@class="success-tip"]/span').text
        self.log(createTime=start_date, activityName=title, cutoffTime=end_date)
        self.send_test_log(logName='新客宝', logType='Run', msg='{} 发布成功'.format(title))
        print(msg)
        # 返回首页继续添加
        self.browser.get(
            'https://work.1688.com/home/page/index.htm?&_path_=sellerBaseNew/2017sellerbase_yingxiao/seller_activitycreator')
        time.sleep(2)

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


if __name__ == '__main__':
    newPassengerTreasure = NewPassengerTreasure()
    newPassengerTreasure.main()
    newPassengerTreasure.quit()
