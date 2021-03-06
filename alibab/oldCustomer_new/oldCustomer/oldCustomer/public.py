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
import json
import time
import requests


class Public(object):

    # 类的初始化
    def __init__(self, account):
        self.account = account
        self.cookie = self.get_cookie()
        self.headers = self.get_headers()
        self.tb_token = self.get_tb_token()
        self.check_cookie()

    # 获取cookie
    def get_cookie(self):
        url = 'http://192.168.1.160:90/alibaba/get_cookie_byaccount?platform=Alibaba'
        response = requests.get(url)
        cookies = json.loads(response.text)
        cookie_dic = {}
        for cookie in cookies:
            # 初始化cookie
            custom_cookie = ''
            # 便利cookie信息
            for i in eval(cookie['cookie_dict_list']):
                # 拼接cookie
                custom_cookie = custom_cookie + i['name'] + '={}; '.format(i['value'])
            # 以键值对的形式存放到字典中
            cookie_dic[cookie['account']] = custom_cookie.strip()
        # 返回指定cookie
        return cookie_dic[self.account]

    # 构造请求头
    def get_headers(self):
        headers = {
            'authority': 'alicrm.alibaba.com',
            # 'method': 'POST',
            # 'path': '/eggCrmQn/crm/customerQueryServiceI/queryCustomerList.json?_tb_token_=f6353a481e533',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            # 'content-length': '98',
            'content-type': 'application/json;charset=UTF-8',
            'cookie': self.cookie,
            'origin': 'https://alicrm.alibaba.com',
            'referer': 'https://alicrm.alibaba.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        return headers

    # 获取 _tb_token_
    def get_tb_token(self):
        tb_token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        tb_token = re.findall(tb_token_re_compile, self.cookie)[0]
        return tb_token

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
        url = 'https://alicrm.alibaba.com/'
        response = requests.get(url, headers=self.headers)
        title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
        title = re.findall(title_re_compile, response.text)[0]
        if title == '客户通':
            pass
        else:
            print('检测cookie 中')
            self.send_test_log(logName='alibaba账号客户列表', logType='Error', msg='{} cookie失效'.format(self.account), position='alibaba账号 {} cookie失效'.format(self.account))
            time.sleep(300)
            self.__init__(self.account)
            self.check_cookie()