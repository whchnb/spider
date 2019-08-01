# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: invite_selenium.py
@time: 2019/5/16 16:13
@desc: 潜客邀约 每日一次，01:00开始
"""
import re
import time
import random
import datetime
import requests
from selenium.webdriver.common.keys import Keys
from DynamicAnnouncement.public_selenium import Public_selenium

class Invite(Public_selenium):

    # 类的初始化
    def __init__(self):
        # 继承父类init 方法
        super(Invite, self).__init__('https://work.1688.com/?_path_=sellerBaseNew/2017sellerbase_yingxiao/daoliinvitationPotential')
        # 获取今日的商品链接
        self.title_list = self.get_products()

    # 首页
    def index(self, invite):
        iframe_element = self.browser.find_element_by_class_name('work-iframe')
        self.browser.switch_to_frame(iframe_element)
        # 若活动为运营店铺粉丝，设置索引为1
        index = 1 if invite == '运营店铺粉丝' else 6
        title_list = self.title_list
        # 点击邀约链接
        self.browser.find_element_by_xpath('//*[@id="app"]/div/div[3]/ul/li[{}]/div[3]'.format(index)).click()
        time.sleep(1)
        # 标题
        title = '新款私模优势出货，送10元卷，欢迎拿样！'
        title_element = self.browser.find_element_by_xpath('//*[@class="next-select next-comobobox large has-clear"]/div/div/input')
        # 全选
        title_element.send_keys(Keys.CONTROL + 'a')
        # 删除
        title_element.send_keys(Keys.DELETE)
        # 添加
        title_element.send_keys(title)
        self.browser.find_element_by_xpath('//*[@class="next-icon next-icon-arrow-up next-icon-medium next-select-arrow"]').click()
        # if index == 1:
        # 点击优惠方式
        self.browser.find_element_by_xpath('//*[@class="inverted-seller-coupon-content-tips"]').click()
        time.sleep(1)
        # 选择优惠券
        self.browser.find_element_by_xpath('//*[@class="coupon-up"][1]').click()
        # 确定优惠券
        self.browser.find_element_by_xpath('//*[@class="main-action-confirm "]').click()
        time.sleep(2)
        # 选择更改商品
        change_element = self.browser.find_element_by_xpath('//*[@class="inverted-seller-offer-content-edit"]')
        self.action.move_to_element(change_element).click().perform()
        for i in range(6):
            try:
                # 删除商品
                self.browser.find_element_by_xpath('/html/body/div[6]/div/div[2]/div[2]/div[2]/div[2]/ul/li[1]/a').click()
            except Exception as e:
                print(e)
                break
        # sku 列表
        sku_list = []
        # 计数器
        count = 0
        for i in range(len(title_list)):
            # 添加5个后，跳出循环
            if count == 5:
                break
            try:
                # 随机选择一个商品
                product = title_list.pop(random.choice(range(len(title_list))))
                # 商品名
                name = product['name']
                print(name)
                # 搜索框输入商品名
                self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(name)
                # 确定搜索
                self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.ENTER)
                time.sleep(0.5)
                # 重复确定
                self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.ENTER)
                time.sleep(1)
                # 添加元素
                add_element = self.browser.find_element_by_xpath('/html/body/div[6]/div/div[2]/div[2]/div[1]/div[2]/ul/li[1]/span[2]')
                self.action.move_to_element(add_element).click().perform()
                # 全选
                self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.CONTROL + 'a')
                # 删除
                self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.DELETE)
                # 计数器+1
                count += 1
                # 添加到列表sku
                sku_list.append(product['sku'])
            except Exception as e:
                print(e)
                self.send_test_log(logName='潜客邀约', logType='Error', msg=str(e), position='添加产品时出错')
        # 点击确定添加的商品
        self.browser.find_element_by_link_text('确认').click()
        time.sleep(1)
        # 发送
        self.browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[4]/div[2]/div/span[1]').click()
        time.sleep(2)
        self.log(invite_type=invite, SKUlist=sku_list)
        self.send_test_log(logName='潜客邀约', logType='Run', msg='{} 发送邀请成功'.format(invite))
        # 取消
        # self.browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[4]/div[2]/div/span[2]').click()
        time.sleep(1)

    # 获取商品
    def get_products(self):
        url = 'http://192.168.1.99:5000/1688/get/tao_huo_yuan/today'
        response = requests.get(url).text
        # 获取每个商品的url 链接
        product_urls_re_complie = re.compile(r'#0000ff;"> <a href="(.*?);">点击查看</a', re.S)
        product_urls = re.findall(product_urls_re_complie, response)
        products_list = []
        for product_url in product_urls:
            # 遍历链接
            try:
                pruduct_dict = self.get_title(product_url)
                if len(pruduct_dict) != 0:
                    products_list.append(pruduct_dict)
            except Exception as e:
                print(e)
                continue
        return products_list

    # 获取商品名及sku
    def get_title(self, url):
        response = requests.get(url, headers=self.headers).text
        title_re_compile = re.compile(r'<meta property="og:title" content="(.*?)"/>', re.S)
        title = re.findall(title_re_compile, response)[0]
        sku_re_compile = re.compile(r'<td class="de-feature">货号</td>.*?<td class="de-value">(.*?)</td>', re.S)
        sku = re.findall(sku_re_compile, response)
        pruduct_dict = {}
        if len(sku) != 0:
            pruduct_dict['sku'] = sku[0]
            pruduct_dict['name'] = title
        return pruduct_dict

    # 日志
    def log(self, invite_type, SKUlist):
        url = 'http://192.168.1.99:90/OSEE/qiankeyaoyuelog'
        data = {
            'Account': 'jakcomcom',
            'Createtime': str(datetime.datetime.now()),
            'invite_type': invite_type,
            'SKUlist': SKUlist,
        }
        response = requests.post(url, data=data)
        print('潜客邀约 {} {}'.format(invite_type, data))
        print(response.text)


if __name__ == '__main__':

    invite_class = [
        '运营店铺粉丝',
        '挖掘潜力大客户'
    ]
    for inv in invite_class:
        invite = Invite()
        invite.index(inv)
        invite.quit()