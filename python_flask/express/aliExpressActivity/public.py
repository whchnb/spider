# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: public.py
@time: 2019/5/25 15:36
@desc:  为alibaba 工作程序提供共用的方法模块
        （包括cookie的获取，请求头的构造，今日需要发布信息的获取，csrf_token的获取，cookie的检测）
"""
import re
import sys
import time
import json
import requests


class Public(object):

    # 类的初始化
    def __init__(self, account):
        self.account = account
        self.cookie = self.get_cookie()
        self.headers = self.get_headers()
        self.check_cookie()

    # 获取cookie
    def get_cookie(self):
        url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
        response = requests.get(url)
        cookies = eval(response.text)
        # 返回指定cookie
        return cookies[self.account]
        # return 'ali_apache_id=183.191.178.30.1557109691539.397124.9; cna=n4lWFZbRW2YCAbe/sh4Lxj33; UM_distinctid=16af89d82063ba-073d310012acd8-e353165-1fa400-16af89d8207d6; aep_common_f=mckH8lUEIe3RmwfCaW/aVfrRSXELiWZaNTTt2pBQffufGrD6FI1IWQ==; _m_h5_tk=54d91e512b56bad46ba9889e9d606e6c_1559212606044; _m_h5_tk_enc=fee06b09394783aa51870c79dfc7ed6c; CNZZDATA1254571644=870484180-1558948231-%7C1559202893; acs_usuc_t=x_csrf=11eb09hctdrj0&acs_rt=d049156d09294e45acbe90345a445d01; xman_us_t=x_lid=jakcomtech&sign=y&x_user=bYv2fhvcBFcFUaV4zTbguA8SGz8EwDsz8vswV+Zk2DA=&ctoken=10p810gy5egtq&need_popup=y&l_source=aliexpress; aep_usuc_t=ber_l=A0; xman_f=8/2bkMEZm6lTkO6OBqUvliw7DzmQRPIDue1JYjJxLWfCbJ2xGFadlJccAEu9np4tfPw/lUS6rZqRRsYucWE9ul7YJKNeskGnKRSRTmMtnZt4RVMxOSkmQTHbT19+H8p5kmesGA7ecFmpWz0yi9gWA4SddlBn0Y2scEwRL4+xEKiAQaHXGCW4L/vQoa1haN8nOSsz0Mrfx2m+HL/8O8cl0LFe0G5aHq1ayXqdce0KVs7HolBlMn36FnhWDy+LtOuC7DofhR65VZ8nQPvt7KtqUgI1iWLtmou9oA+Af9KiRqX05Xqd9jZv2bTz+F16HIdJXC5LtJc26Bo060Odocz8EBhHzXaJhfPvWeCHv34xWMNI+aHzXy9G1BlB7trJPM8kU12VY+cs5jWfA+DC2+Bwhg==; ali_apache_track=ms=|mt=2|mid=jakcomtech; ali_apache_tracktmp=W_signed=Y; xman_us_f=zero_order=y&x_locale=zh_CN&x_l=1&last_popup_time=1557109691567&x_user=CN|Ady|Cao|cnfm|229737297&no_popup_today=n; intl_locale=zh_CN; aep_usuc_f=isfm=y&c_tp=USD&ispm=y&x_alimid=229737297&iss=y&s_locale=zh_CN&region=US&b_locale=en_US; _uab_collina=155921411692666217176183; _umdata=G282AA9260EB76ED2F44C5C50B4F02B62A8CB81; l=bBNV8y27v7TLxgjzBOCwIuI8LS7TYIRAguPRwCbDi_5QO6YX0b_OlH2WDFv6Vj5RsFLB4s6vWje9-etki; isg=BCYmiXVFRl7W1hL5l5sy6Hmxd5xor2tBwFpJyhDPTck2k8ateJSD0P5h748fO2LZ; JSESSIONID=194FAEF8200FD2FECE7BA7EEC27085F1; xman_t=1+mul+dUj94cMmLi3aPas9zxEkR5UrktrUlrfc8VcZIvj2yefWIC28p9UIQN5kAx7QksDce37yamMatv1c+L1tfaHy4fnmSE9tuM71ryPX4ZL9iLz14olwUX/EBYT268cMsO3N5FAcI3M+B6AbhSJWnMYBHPjZQr3rD1w9UA4/0L+HytjWJMDXovqVIsE8p84ekjVlR+Kwatv0gDn8J+jXgOLYwpyYrDjKnYZrRVhcdfJbRqAPzsrz1ZaYQ3M8OkRPj2yUHCiFU0VNpWtSLQ202EOus/ZE/XwR2fLbzY5tkB0dbnujuCSnG1JxPM4ADtMRsw1+9WJbAFCGLQHUtdJFUOo2EaDDy6ZPBfyD+OxhqyqrLDzLF/MDBy0qulYqMrN1/dvKVj45ioEBdcQfca7ZAVJ50lsWw4VkOcJUpKF8YwqusnG5Wtxq35wR30WJfLdBjZGykGy0h4YExEdFDzwUlOgc0EK3wBGenrDc/qZvjsDd+0TgIr1UH3JilHKHUnL6FK72xdtOI2Gq9tu/0xFKd3kihgbXl0N1Z1XW59Bfq2AlH+GyjsGfICT0ThwK8No/LuQcCANaFIFHBvvSonIR62guYO4CjBYfi+sAAccuYDd+vs1piIJmartEJWXCMTH2S+Gc0fWFWaK+w5QDfkgA==; intl_common_forever=BPc8pTB1cSo+44HPPYtmMfCHm4AqgZyx296YQytYeLaIoJ7CFuVmbQ=='
    # 构造请求头
    def get_headers(self):
        headers = {
             'authority': 'mypromotion.aliexpress.com',
            'origin': 'https://mypromotion.aliexpress.com',
            'referer': 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm?spm=5261.10636610.200.12.4b8a3e5fDy3Y8L',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'scheme': 'https',
            'accept-encoding': 'gzip, deflate, br',
            'upgrade-insecure-requests': '1',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'cookie': self.cookie,
            'cache-control': 'max-age=0',
        }
        return headers

    # 获取 _tb_token_
    def get_tb_token(self):
        tb_token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        tb_token = re.findall(tb_token_re_compile, self.cookie)[0]
        return tb_token

    def get_csrf_token(self):
        url = 'http://photobank.aliexpress.com/photobank/uploader-new.htm'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r"csrfToken:'(.*?)'", re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.text)[0]
        return csrf_token

    def get_ctoken(self):
        try:
            ctoken_re_compile = re.compile(r'ctoken=(.*?)&', re.S)
            ctoken = re.findall(ctoken_re_compile, self.cookie)[0]
        except:
            ctoken_re_compile = re.compile(r'ctoken=(.*?);', re.S)
            ctoken = re.findall(ctoken_re_compile, self.cookie)[0]
        return ctoken

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

    # cookie 的检测
    def check_cookie(self):
        url = 'https://sellercenter.aliexpress.com/seller/index.htm'
        response = requests.get(url, headers=self.headers)
        title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
        title = re.findall(title_re_compile, response.text)[0]
        if 'Manufacturer' in title:
            pass
        else:
            self.send_test_log(logName='速卖通管理cookie失效', logType='Error', msg='{} cookie失效'.format(self.account), position='alibaba账号 {} cookie失效'.format(self.account))
            time.sleep(300)
            self.__init__(account=self.account)
            self.check_cookie()

    def log(self, data):
        post_data = {
            'Account': data['Account'],
            'Promotion_type': data['Promotion_type'],
            'Channel': data['Channel'],
            'Promotion_Name': data['Promotion_Name'],
            'Begin_time': data['Begin_time'],
            'End_time': data['End_time'],
            'ProductID': data['ProductID']
        }
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/promotion_save'
        response = requests.post(url, data=post_data)
        print(response)
        print(response.text)

    def coupon_log(self, data):
        post_data = {
            'Account': data['Account'],
            'coupontype': data['coupontype'],
            'Starttime': data['Starttime'],
            'activityname': data['activityname'],
            'nominal_value': data['nominal_value'],
            'Condition': data['Condition'],
            'Endtime': data['Endtime'],
        }
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/coupon_logger'
        response = requests.post(url, data=post_data)
        print(response)
        print(response.text)


