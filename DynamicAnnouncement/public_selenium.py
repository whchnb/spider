# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: public_selenium.py
@time: 2019/5/16 10:58
@desc:
"""
import re
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from DynamicAnnouncement.public import Public
from selenium.webdriver.common.action_chains import ActionChains


class Public_selenium(Public):

    # 类的初始化
    def __init__(self, url):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        super(Public_selenium, self).__init__()
        # 请求目标链接
        self.url = url
        # 构造浏览器对象
        self.browser = self.launch_web()
        self.action = ActionChains(self.browser)
    #  启动无头浏览器
    def launch_web(self):
        """
        启动无头浏览器
        :return: 浏览器对象
        """
        print('正在启动浏览器')
        # 浏览器设置
        chrome_options = Options()
        # 设置无头
        # chrome_options.add_argument('--headless')
        # 加上这个属性来规避bug
        chrome_options.add_argument('disable-gpu')
        # 设置浏览器分辨率
        # chrome_options.add_argument('window-size=1200,1100')
        # 不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 配置浏览器
        # chrome_options.add_experimental_option("prefs", prefs)
        # 启动浏览器
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.maximize_window()
        # 使用浏览器打开链接
        browser.get(self.url)
        # 删除浏览器生成的cookie
        browser.delete_all_cookies()
        # 获取账户对应cookie
        cookie_list = self.get_selenium_cookie()
        # cookie_list = [{'name': 'UM_distinctid', 'value': '16a8b52b22d7d-059d3153703b06-e323069-1fa400-16a8b52b22e3a3', 'domain': '.1688.com'}, {'name': 'cna', 'value': 'n4lWFZbRW2YCAbe/sh4Lxj33', 'domain': '.1688.com'}, {'name': 'ali_apache_id', 'value': '11.186.201.38.1557135135792.051504.0', 'domain': '.1688.com'}, {'name': 'lid', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': 'ali_apache_track', 'value': 'c_mid', 'domain': '.1688.com'}, {'name': '_umdata', 'value': 'G282AA9260EB76ED2F44C5C50B4F02B62A8CB81', 'domain': '.1688.com'}, {'name': '__utma', 'value': '62251820.53433343.1557966739.1557966739.1557966739.1', 'domain': '.1688.com'}, {'name': '__utmz', 'value': '62251820.1557966739.1.1.utmcsr', 'domain': '.1688.com'}, {'name': 'ali_ab', 'value': '183.191.179.144.1557982246155.1', 'domain': '.1688.com'}, {'name': 'h_keys', 'value': '"airpods#%u7b14%u8bb0%u672c%u7535%u8111#%u4eca%u65e5%u7279%u4ef7%u4ea7%u54c1%u63a8%u8350"', 'domain': '.1688.com'}, {'name': 'ad_prefer', 'value': '"2019/05/17 17:14:07"', 'domain': '.1688.com'}, {'name': 'XSRF-TOKEN', 'value': '439222b9-203c-4eec-ace0-e80df19f2574', 'domain': '.1688.com'}, {'name': 'cookie2', 'value': '19b7fc93fef75fa8606d3a6e445f6a09', 'domain': '.1688.com'}, {'name': 't', 'value': '1f71f19a13a626847bf3376cbfa1cbe0', 'domain': '.1688.com'}, {'name': '_tb_token_', 'value': 'ef3733b6e9097', 'domain': '.1688.com'}, {'name': '__cn_logon__', 'value': 'true', 'domain': '.1688.com'}, {'name': '__cn_logon_id__', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': 'ali_apache_tracktmp', 'value': 'c_w_signed', 'domain': '.1688.com'}, {'name': 'last_mid', 'value': 'b2b-2257499635', 'domain': '.1688.com'}, {'name': 'ctoken', 'value': 'kyN0MeiOkXxS5dO88Gvrcoco', 'domain': '.1688.com'}, {'name': 'cookie1', 'value': 'BxoD8yON%2BLKP2nR%2FU%2BsuODsyQQ7FVtqL2homXzhyRFg%3D', 'domain': '.1688.com'}, {'name': 'cookie17', 'value': 'UUpkv67HfD0F4g%3D%3D', 'domain': '.1688.com'}, {'name': 'sg', 'value': 'm53', 'domain': '.1688.com'}, {'name': 'csg', 'value': '82d796ca', 'domain': '.1688.com'}, {'name': 'unb', 'value': '2257499635', 'domain': '.1688.com'}, {'name': '_nk_', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': '_csrf_token', 'value': '1558519010993', 'domain': '.1688.com'}, {'name': '_is_show_loginId_change_block_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_force_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_sys_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_user_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '__rn_alert__', 'value': 'false', 'domain': '.1688.com'}, {'name': 'alicnweb', 'value': 'touch_tb_at%3D1558519020097%7Clastlogonid%3Djakcomcom%7Cshow_inter_tips%3Dfalse', 'domain': '.1688.com'}, {'name': 'l', 'value': 'bBM41yPPvD94RXr2KOfwSuI8LS7tEIRbzsPzw4OgiICP_IWM5M_PWZtWS9xHC3GVa6nDJ3kM34SXBcY7ryznh', 'domain': '.1688.com'}, {'name': 'isg', 'value': 'BEJCISftqvg2lbaOQ7ogMIulk0hku0etnt4f34xbqLVg3-BZdafCPFldi5sGj77F', 'domain': '.1688.com'}]
        for cookie in (cookie_list):
            # 将cookie添加到浏览器中
            browser.add_cookie({'name': cookie['name'], 'domain': cookie['domain'], 'value':cookie['value']})
        print('cookie 更改成功')
        # 重新打开链接
        browser.get(self.url)
        time.sleep(1)
        return browser

    # 获得selenium 所需要的cookie
    def get_selenium_cookie(self):
        """
        获得selenium 所需要的cookie
        :return: cookie 列表
        """
        # 获取cookie 的链接
        cookie_url = 'http://192.168.1.190:5000/1688/get/cookies/jakcomcom'
        response = requests.get(cookie_url)
        # 获取cookie 的正则表达式
        cookies = eval(response.text)
        # 初始化cookie
        custom_cookie = ''
        cookiesDict = {}
        cookieList = []
        for cookie in cookies:
            # 构造cookie
            for i in cookie[7].split(';'):
                cookiesDict[i.split('=')[0]] = i.split('=')[1]
        for k, v in cookiesDict.items():
            c = {}
            c['domain'] = '.1688.com'
            c['name'] = k
            c['value'] = v
            cookieList.append(c)
            # custom_cookie = custom_cookie + cookie['name'] + '={}; '.format(cookie['value'])
        # 返回构造好的cookie
        return cookieList

    def quit(self):
        self.browser.quit()