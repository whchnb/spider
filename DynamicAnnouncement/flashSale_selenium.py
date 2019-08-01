# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: flashSale_selenium.py
@time: 2019/5/16 20:15
@desc: 限时促销 每日一次，01:00开始 删除过期活动
"""
import re
import json
import time
import random
import requests
import datetime
from selenium.webdriver.common.keys import Keys
from DynamicAnnouncement.public_selenium import Public_selenium


class FlashSale(Public_selenium):

    # 类的初始化
    def __init__(self):
        # 继承父类的init 方法
        super(FlashSale, self).__init__('https://work.1688.com/?_path_=sellerBaseNew/2017sellerbase_yingxiao/limitDiscount')
        # 构造iframe 元素
        iframe_element = self.browser.find_element_by_class_name('work-iframe')
        # 选择iframe 元素
        self.browser.switch_to_frame(iframe_element)

    # 删除过期活动
    def delete_expired(self):
        # 选择过期的所有元素
        expireds = self.browser.find_elements_by_xpath('//*[@class="activity ended"]')
        # 便利过期元素
        for expired in expireds:
            # 删除
            self.browser.find_element_by_link_text('删除').click()
            # 确认删除
            self.browser.find_element_by_link_text('确认').click()
            time.sleep(1)

    # 首页
    def index(self):
        time.sleep(1)
        try:
            # 选择添加活动，若存在旧活动，则点击
            self.browser.find_element_by_xpath('//*[@class="button create-activity"]').click()
        except Exception as e:
            print(e)
            self.send_test_log(logName='限时促销', logType='Error', msg='可能没有旧活动 {}'.format(str(e)))
        finally:
            time.sleep(1)
            # 标题
            title = '今日特价'
            # 写入标题
            self.browser.find_element_by_xpath('//*[@class="input input-large show-bubble activity-name"]').send_keys(title)
            # 点击起始时间框
            self.browser.find_element_by_xpath('//*[@class="input input-large datepicker start-date"]').click()
            # 选择开始时间
            self.browser.find_element_by_xpath('//*[@class="ok"]').click()
            # 点击结束时间
            self.browser.find_element_by_xpath('//*[@class="input input-large datepicker end-date"]').click()
            # 现在的时间
            date = datetime.datetime.now()
            # 现在的年
            now_year = date.year
            # 现在的月份
            now_month = date.month
            # 7天后的年
            week_year = (date + datetime.timedelta(days=7)).year
            # 7天后的月份
            week_month = (date + datetime.timedelta(days=7)).month
            # 7天后的日期
            week_day = (date + datetime.timedelta(days=7)).day
            # 如果7天后的月份大于现在的月份或者7天后为下一年
            if week_month > now_month or week_year > now_year:
                # 点击下一页
                self.browser.find_element_by_xpath('//*[@class="next "]').click()
            # 获取日期所有元素
            days_element = self.browser.find_elements_by_xpath('//*[@class="dbd fd-clr"]/a')
            # 便利
            for index, day_element in enumerate(days_element):
                # 若遍历到7天后的日子
                if week_day == int(day_element.text):
                    # 点击
                    day_element.click()
            # 确定起始时间
            self.browser.find_element_by_xpath('//*[@class="ok"]').click()
            # 选择优惠方式
            self.browser.find_element_by_xpath('//*[@id="way-discount-type"]').click()
            # 选择优惠商品
            self.browser.find_element_by_link_text('请选择').click()
            count = 0
            # 获取今日优惠商品
            products = self.get_product()
            # sku列表
            sku_list = []
            for product in products:
                # 若选择了10个产品则返回
                if count == 10:
                    break
                try:

                    # 商品名称
                    name = product['Subject']
                    # 选择搜索框
                    search_element = self.browser.find_element_by_xpath('//*[@class="input keywords"]')
                    # 全选检索框
                    search_element.send_keys(Keys.CONTROL + 'a')
                    # 删除
                    search_element.send_keys(Keys.DELETE)
                    # 输入检索名称
                    search_element.send_keys(name)
                    # 确认搜索
                    search_element.send_keys(Keys.ENTER)
                    time.sleep(1)
                    # 选择商品
                    self.browser.find_element_by_link_text('选择').click()
                    # 全选检索框
                    search_element.send_keys(Keys.CONTROL + 'a')
                    # 删除
                    search_element.send_keys(Keys.DELETE)
                    # 将添加好的商品sku 存放起来
                    sku_list.append(product['SKU'])
                    # 计数器 + 1
                    count += 1
                except Exception as e:
                    self.send_test_log(logName='限时促销', logType='Error', msg=str(e), position='选择添加商品')
                    continue
            # 点击保存
            self.browser.find_element_by_link_text('保存').click()
            # 输入优惠折扣
            self.browser.find_element_by_xpath('//*[@class="input input-large show-bubble discount-rate"]').send_keys('8.8')
            # 点击确定
            self.browser.find_element_by_link_text('确定').click()
            # 确认创建活动
            self.browser.find_element_by_link_text('创建活动').click()
            # 写入日志
            self.send_test_log(logName='限时优惠', logType='Run', msg='成功发布限时优惠')
            self.log(limitname=title, SKUlist=sku_list)

    # 获取商品
    def get_product(self):
        url = 'http://cs1.jakcom.it/OSEE/Limit_productdata'
        response = requests.get(url)
        datas = json.loads(response.text)
        random.shuffle(datas)
        return datas

    # 日志
    def log(self, limitname, SKUlist):
        url = 'http://192.168.1.99:90/OSEE/Limitlog'
        data = {
            'Account': 'jakcomcom',
            'Createtime': str(datetime.datetime.now()),
            'limitname': limitname,
            'SKUlist': SKUlist
        }
        print('限时优惠', data)
        response = requests.post(url, data)
        print(response.text)


if __name__ == '__main__':
    flash = FlashSale()
    flash.delete_expired()
    flash.index()
    flash.quit()