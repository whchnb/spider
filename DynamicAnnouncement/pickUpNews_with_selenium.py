# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: pickUpNews_with_selenium.py
@time: 2019/5/14 18:06
@desc: 每天00:10 定时发布挑货动态
"""
import re
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from DynamicAnnouncement.public_selenium import Public_selenium


class PickUpNews(Public_selenium):

    # 类的初始化
    def __init__(self):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        super(PickUpNews, self).__init__('https://work.1688.com/?_hex_name=%E5%95%86%E5%93%81%E6%B8%85%E5%8D%95&_hex_type=offerlist&_path_=sellerBaseNew/2017Sellerbase_Customer/createDynamic')

    # 获取商品的图片链接，商品名称以及商品价格
    def get_img_price(self, url):
        """
        获取商品的图片链接，商品名称以及商品价格
        :param url: 获取信息的目标链接
        :return: 商品的图片链接，商品名称以及商品价格
        """
        response = requests.get(url, headers=self.headers, verify=False)
        # 构造获取信息的匹配规则
        re_str = '<a class="box-img".*?hidefocus="true">.*?<img src="(.*?)" alt="(.*?)"/>'
        # 构造获取信息的正则匹配对象
        data_re_complie = re.compile(re_str, re.S)
        data = re.findall(data_re_complie, response.text)[0]
        # 获取商品图片链接，商品名称
        imageUrl, offerTitle = data
        image_list = imageUrl.split('.')
        image_list [-2] = '120x120'
        # 为图片添加指定大小
        imageUrl = '.'.join(image_list)
        # 获取商品价格
        price = re.findall(re.compile(r'"begin":"1000","end":"","price":"(.*?)"', re.S), response.text)[0]
        # 返回商品的图片链接，商品名称以及商品价格
        return imageUrl, offerTitle, price

    # 提交信息
    def submit(self):
        """
        提交信息
        """
        # 构造日期
        date = str(datetime.datetime.now().date()).replace('-', '')
        # 构造内容
        content = '今日特价「{}期」，全天八折优惠，满50减10，满100减20。'.format(date)
        # 构造标题
        title = '今日特价「{}期」'.format(date)
        # 在指定位置输入内容
        self.browser.find_element_by_xpath('//*[@id="__hex__"]/div/div/div[2]/div[4]/div/div/div/div[2]/div[1]/div/div[3]/div[1]/div[2]/div/textarea').send_keys(content)
        # 在指定位置输入标题
        self.browser.find_element_by_xpath('//*[@id="__hex__"]/div/div/div[2]/div[4]/div/div/div/div[2]/div[1]/div/div[4]/div/div/textarea').send_keys(title)
        # 点击添加商品
        self.browser.find_element_by_xpath('//*[@class="picture-add product-add"]').click()
        # 获取今天需要发送动态的商品
        product_list = self.get_products()
        # 遍历每个商品
        for product in product_list:
            # 获取商品id
            product_id = product['product']['id']
            # 拼接商品链接
            offerUrl = "https://detail.1688.com/offer/{}.html".format(product_id)
            # 获取商品图片链接，名称，价格
            imageUrl, offerTitle, price = self.get_img_price(offerUrl)
            # 通过商品名称进行检索
            self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(offerTitle)
            # 确认检索
            self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.ENTER)
            self.browser.implicitly_wait(30)
            time.sleep(1)
            # 点击添加商品
            self.browser.find_element_by_xpath('/html/body/div[4]/div/div[2]/div[2]/div[1]/div[2]/ul/li/span[2]').click()
            self.browser.implicitly_wait(30)
            # 全选检索框
            self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.CONTROL + 'a')
            # 删除检索内容
            self.browser.find_element_by_xpath('//*[@class="input-keywords"]').send_keys(Keys.DELETE)
        # 点击确认按钮
        self.browser.find_element_by_xpath('//*[@class="btn-submit-confirm"]').click()
        time.sleep(1)
        # 勾选服务准则
        self.browser.find_element_by_xpath('//*[@class="next-checkbox-label"]/span').click()
        time.sleep(1)
        try:
            # 点击发布
            self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-primary next-btn-large"]').click()
            self.send_log(channel='挑货动态', products=product_list, createtime=(datetime.datetime.now()))
        except Exception as e:
            self.send_test_log(logName='挑货动态', logType='Error', msg='发布失败 ' + str(e))
        finally:
            time.sleep(5)


if __name__ == '__main__':
    pickUpNews = PickUpNews()
    pickUpNews.submit()
    pickUpNews.quit()