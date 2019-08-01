# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: public.py
@time: 2019/5/14 13:42
@desc:  为
        announce.py 淘货源公告
        microDynamic.py 微供动态
        pickUpNews_with_selenium.py 挑货动态
        提供共用的方法模块（包括cookie的获取，请求头的构造，今日需要发布信息的获取，csrf_token的获取）
@uploadtime:2019/5/22
@desc:  增加检测cookie是否可用，以及将执行成功后的状态写入本地
"""
import re
import sys
import json
import datetime
import requests


class Public(object):

    # 类Public 的初始化
    def __init__(self):
        """
        类Public 的初始化
        """
        self.cookie = self.get_cookie()
        self.headers = self.get_headers()
        self.check_cookie()

    # 构造请求头
    def get_headers(self):
        """
        构造请求头
        :return: 构造完成的请求头
        """
        headers = {
            'authority': 'channel.1688.com',
            'path': '/page/bulletinpublish.htm',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'cookie': self.cookie,
            'referer': 'https://channel.1688.com/page/bulletinlist.htm',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        }
        return headers

    # 获取cookie
    def get_cookie(self):
        """
        获取cookie
        :return: 构造好的cookie
        """
        # 获取cookie 的链接
        cookie_url = 'http://192.168.1.190:5000/1688/get/cookies/jakcomcom'
        response = requests.get(cookie_url)
        # 获取cookie 的正则表达式
        cookies = eval(response.text)
        # 初始化cookie
        custom_cookie = ''
        cookiesDict = {}
        for cookie in cookies:
            # 构造cookie
            for i in cookie[7].split(';'):
                cookiesDict[i.split('=')[0]] = i.split('=')[1]
        for k, v in cookiesDict.items():
            custom_cookie = custom_cookie + k + '=' + v + '; '
            # custom_cookie = custom_cookie + cookie['name'] + '={}; '.format(cookie['value'])
        # 返回构造好的cookie
        return custom_cookie
        # return 'UM_distinctid=16a8b52b22d7d-059d3153703b06-e323069-1fa400-16a8b52b22e3a3; cna=n4lWFZbRW2YCAbe/sh4Lxj33; ali_apache_id=11.186.201.38.1557135135792.051504.0; lid=jakcomcom; ali_apache_track=c_mid=b2b-2257499635|c_lid=jakcomcom|c_ms=2|c_mt=2; _umdata=G282AA9260EB76ED2F44C5C50B4F02B62A8CB81; __utma=62251820.53433343.1557966739.1557966739.1557966739.1; __utmz=62251820.1557966739.1.1.utmcsr=fuwu.1688.com|utmccn=(referral)|utmcmd=referral|utmcct=/promotion/shangjizhuli/2017/loading.html; ali_ab=183.191.179.144.1557982246155.1; h_keys="airpods#%u7b14%u8bb0%u672c%u7535%u8111#%u4eca%u65e5%u7279%u4ef7%u4ea7%u54c1%u63a8%u8350"; ad_prefer="2019/05/17 17:14:07"; XSRF-TOKEN=439222b9-203c-4eec-ace0-e80df19f2574; cookie2=19b7fc93fef75fa8606d3a6e445f6a09; t=1f71f19a13a626847bf3376cbfa1cbe0; _tb_token_=ef3733b6e9097; __cn_logon__=true; __cn_logon_id__=jakcomcom; ali_apache_tracktmp=c_w_signed=Y; last_mid=b2b-2257499635; ctoken=kyN0MeiOkXxS5dO88Gvrcoco; cookie1=BxoD8yON%2BLKP2nR%2FU%2BsuODsyQQ7FVtqL2homXzhyRFg%3D; cookie17=UUpkv67HfD0F4g%3D%3D; sg=m53; csg=82d796ca; unb=2257499635; _nk_=jakcomcom; _csrf_token=1558519010993; _is_show_loginId_change_block_=b2b-2257499635_false; _show_force_unbind_div_=b2b-2257499635_false; _show_sys_unbind_div_=b2b-2257499635_false; _show_user_unbind_div_=b2b-2257499635_false; __rn_alert__=false; alicnweb=touch_tb_at%3D1558519020097%7Clastlogonid%3Djakcomcom%7Cshow_inter_tips%3Dfalse; l=bBM41yPPvD94RXr2KOfwSuI8LS7tEIRbzsPzw4OgiICP_IWM5M_PWZtWS9xHC3GVa6nDJ3kM34SXBcY7ryznh; isg=BEJCISftqvg2lbaOQ7ogMIulk0hku0etnt4f34xbqLVg3-BZdafCPFldi5sGj77F'

    # 获取今日所需发布的信息
    def get_content(self):
        """
        获取今日所需发布的信息
        :return: 今日所需发布的信息
        """
        # 获取今日所需发布的内容链接
        content_url = 'http://192.168.1.190:5000/1688/get/tao_huo_yuan/today'
        response = requests.get(content_url)
        # 获取今日所需发布的信息
        content = eval(response.text)
        return content

    # 获取token
    def get_token(self, re_str, token_url):
        """
        获取token
        :param re_str: 获取token 的正则表达式
        :param token_url:  需要获取token 的目标链接
        :return: token
        """
        response = requests.get(token_url, headers=self.headers, verify=False)
        # 构造所需要的token
        token_re_complie = re.compile(re_str, re.S)
        try:
            token = re.findall(token_re_complie, response.text)[0]
        except Exception as e:
            print('即将退出程序,token获取失败，请检查cooke')
            self.send_test_log(logName='public', logType='Error', msg='token获取失败，请检查cooke' + str(e))
            sys.exit()
        # 返回token
        return token

    # 获取product 列表
    def get_products(self):
        """
        \获取product 列表
        :return: product 列表
        """
        products = self.get_content()
        product_list = [
            {
                'product': {
                    'id': products['product_id_1'],
                    'name': products['product_name_1']
                }
            },
            {
                'product': {
                    'id': products['product_id_2'],
                    'name': products['product_name_2']
                }

            }
        ]
        # 返回商品列表
        return product_list

    # 日志
    def send_log(self, channel, products, createtime):
        log_url = 'http://192.168.1.160:90/OSEE/NoticeWrite'
        for product in products:
            subject = product['product']['name']
            ProductID = product['product']['id']
            data = {
                'channel': channel,
                'subject': subject,
                'ProductID': ProductID,
                'Createtime': createtime
            }
            response = requests.post(log_url, data=data)
            print(response.text)

    # 发送测试日志
    def send_test_log(self, logName,logType, msg, position='0'):
        msg = str(msg)
        test_url = 'http://192.168.1.160:90/Log/Write'
        data = {
            'LogName': logName,
            'LogType': logType,
            'Position': position,
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': msg,
        }
        test_response = requests.post(test_url, data=data)
        print('test_response', test_response.text)

    # 检测cookie 是否可以使用
    def check_cookie(self):
        response = requests.get(url='https://work.1688.com/home/page/index.htm', headers=self.headers)
        title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
        title = re.findall(title_re_compile, response.text)
        # print(response.text)
        if '1688-卖家工作台' not in title:
            self.send_test_log(logName='Jakcomcom', logType='Error', msg='jakcomcom cookie 失效',
                               position='jakcomcom cookie 失效')
            # raise ValueError('The cookie has expired. Please try again later')
a = Public()