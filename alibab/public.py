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
import datetime
import requests


class Public(object):

    # 类的初始化
    def __init__(self, account):
        self.account = account
        self.headers = self.get_headers()
        self.cookie = self.get_cookie()
        # self.tb_token = self.get_tb_token()

    # 获取cookie
    def get_cookie(self):
        url = 'http://192.168.1.160:90/alibaba/get_cookie_byaccount?platform=Alibaba'
        response = requests.get(url)
        # 获取cookie 的正则表达式
        cookies = json.loads(response.text)
        for cookie in cookies:
            # 构造cookie
            if cookie['account'] != self.account or cookie['cookies'] is None:
                continue
            # return 'ali_apache_id=11.179.217.87.1557109662927.980741.2; t=0ec389e5303cc4ad299e6c6d2807925d; cna=n4lWFZbRW2YCAbe/sh4Lxj33; gangesweb-buckettest=183.191.178.30.1557109697018.0; UM_distinctid=16a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432; _ga=GA1.2.1933742769.1557196023; _bl_uid=jqjdRvhhfmn0F5ijwkypan8gdsn8; _umdata=G282AA9260EB76ED2F44C5C50B4F02B62A8CB81; last_ltc_icbu_icbu=cHdk; sc_g_cfg_f=sc_b_currency=CNY&sc_b_locale=en_US&sc_b_site=CN; uns_unc_f=trfc_i=safcps^bnv96bor^in7r61t0^1dec1uncc; cn_1262570533_dplus=%7B%22distinct_id%22%3A%20%2216a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201561777908%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201561777908%2C%22initial_view_time%22%3A%20%221561775548%22%2C%22initial_referrer%22%3A%20%22https%3A%2F%2Fpost.alibaba.com%2Fproduct%2Fpublish.htm%3FcatId%3D5093099%22%2C%22initial_referrer_domain%22%3A%20%22post.alibaba.com%22%7D; __utma=226363722.1933742769.1557196023.1563261562.1563261562.1; __utmz=226363722.1563261562.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); acs_usuc_t=acs_rt=7ed7d2cbb48d4143a083b8cce16498f4; cookie2=1879435292a8c6ace568b56e8a66c965; _tb_token_=ee8353ee1016e; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1560769958437&x_user=CN|Ady|JAKCOM|cgs|222438073&no_popup_today=n; intl_locale=zh_CN; ali_apache_tracktmp=W_signed=Y; _csrf_token=1564192111666; JSESSIONID=413D83F7595005E724F46A7AE60F1826; _hvn_login=4; csg=e23e45a1; l=cBQ0s6OIvqLqgLQ9BOCNCuI8LS7ORIRfguPRwCbDi_5B91T6d17OkVYQae96cjWFGkTH4k6UXweT0UH_-ykjsVADjoIxZG1..; isg=BJubqkauQhlff78quFYbE_RYKv_F2K7yuXc0vY3YWhqxbLpOF0Siw8auAozHzAdq; ali_apache_track=mt=3|mid=cn1512437204; xman_us_t=ctoken=18bi5ndogjod8&l_source=alibaba&x_user=YA3eyuex13KSerhKfvdaz0RcL0+jMw/2A4pHGTBxrRg=&x_lid=cn1512437204&sign=y&need_popup=y; xman_t=eTgs/AdK1NnXv9CRK11euFiYDMNHicK4k0aZ5iIkzB9bezSru/oPiHUq/muzz3PP2zDq7C+u/mRgyLb6Ey54eJB6gdpE2/sWC+uK4UBU0MHPlxycfOvtLBiD7xDhxO4vIGbyJk+EpDcFnZDnyZ3xSpb460ckj3t+6UgEskNxNeC5WkbFHaec/h70w9XEyXre5KK39EeBPq36b9aSJqs/OR0X2Vc/2nqS4zuTrpH3so5qym+XtpH9BXrpN8UJmD/4c0BhO5X/iklyZVuUmE5bxAx1wi9svuCCREGSUV+nPbmhIOtTfVPkpxNhyq84cbL0Ruh7E5dGKh3gKuV9+PHnaa50CAKZgkQSHLilcBdCDPpHkE89EWJVFhylVjQ+dwsGJHFY3wrGDVkBTUJKokyMsvrIzF3kcBYF1wNsZyu1/T+Y0j/Jh8fTlIsbu5RHqCUEwBa1Qyp/rMiaMLg0q6ngXtTOSTJGNvMUkSW1rdHucOvptj3wXtB/mxhyUT5xAup1YajN824Ltrd2NtcGMzCHyTHUve+fQnOTXJW+KrJn+qX4AdCZdNVElHrBa22uQ+OXlbfbrdLAJbRXwpDbGURW2gqIH7TXz3435aMmcWBSWPgkqSZNDVvapjirhRmEs5xBtpJ6SrYihqdjec+Y601yqT6FnGEDYAxYs5Oa5dZ4r3gKgYg/9QPcrA==; intl_common_forever=PO0BqiCD9F2XrIrTrLaDjNWW8oFm95HHxvNUe4LPS4qRKrv+E4bxM4XIHMhIq3BVvG5Ls9M38oxvHvUa0rbI25/Cp9hy5vx8abR27c8VVIU=; xman_f=86Y4zmbLpRKvDfCAay83+BZ9VU4BLMu3Sb2Qq42Fq+OoWpOZ0eNe7aD5u8tQ+BF3Pg6cnZsMct8vDnjXhUrhArhsagyy9c9wxBkX3DA+bgFqzVplvlTsdTuM9/q8u3KG+6LElm9dZeIhDAS4eCzGnjcUhCESuL1tMPPp5K42MQNE6Y5j5A1jc44tKefmp3XldHXg2kM9Wvhke8ohElVJrGm7zUXKGeKMrnbCeGBSOwWtDoSGZL6g8EQEdniUasPN+4gT85q7w3yJenasIL0bvQ77HwsofUdY5I+yiHzudCIeamhpORawDkD9z8gmsHNy81m+NIj1NnMqvlfxe9dJasJ+nCuAY91JEd2tdtwnvXCF3Qy3jpGlMkH6VdmMPHTSCjJhTbpaS14='
            cook = cookie['cookies']
            self.headers['cookie'] = cook
            status = self.check_cookie()
            print(status)
            if status is True:
                return cook
            else:
                continue

    # 构造请求头
    def get_headers(self):
        headers = {
            # 'authority': 'alicrm.alibaba.com',
            # 'method': 'POST',
            # 'path': '/eggCrmQn/crm/customerQueryServiceI/queryCustomerList.json?_tb_token_=f6353a481e533',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            # 'content-length': '98',
            'content-type': 'application/json;charset=UTF-8',
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

    def get_csrf_token(self):
        url = 'http://photobank.aliexpress.com/photobank/uploader-new.htm'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r"csrfToken:'(.*?)'", re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.text)[0]
        return csrf_token

    def get_ctoken(self):
        ctoken_re_compile = re.compile(r'ctoken=(.*?)[;&]', re.S)
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
        url = 'https://alicrm.alibaba.com/'
        response = requests.get(url, headers=self.headers)
        title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
        title = re.findall(title_re_compile, response.text)[0]
        print(title)
        if title == '客户通':
            return True
        else:
            self.send_test_log(logName='alibaba账号', logType='Error', msg='{} cookie失效'.format(self.account), position='alibaba账号 {} cookie失效'.format(self.account))
            return False
# Public('fb2@jakcom.com')
# print(Public('fb2@jakcom.com').get_ctoken())
