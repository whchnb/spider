# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request


class OldcustomerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class OldcustomerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


import re
import sys
import json
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
            self.send_test_log(logName='alibaba账号', logType='Error', msg='{} cookie失效'.format(self.account), position='alibaba账号 {} cookie失效'.format(self.account))
            sys.exit()

#
# class RequestCustomer(Request):
#
#     def __init__(self,account,*args, **kwargs):
#         super(RequestCustomer, self).__init__(account)
#
#
#
#
# class HeadersDownloadMiddleware(object):
#     def process_request(self, request, spider, account):
#         public = Public(account)
#         request.headers = public.headers


