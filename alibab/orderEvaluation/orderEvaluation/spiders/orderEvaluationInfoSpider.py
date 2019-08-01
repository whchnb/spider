# -*- coding: utf-8 -*-
import json
import scrapy
from xml.etree import ElementTree
from urllib.parse import urlencode
from alibaba.productAnalysis.productAnalysis.public import Public


class OrderevaluationinfospiderSpider(scrapy.Spider):
    name = 'orderEvaluationInfoSpider'
    allowed_domains = ['fb.alibaba.com']
    start_urls = ['http://fb.alibaba.com/']

    def start_requests(self):
        account_list = [
            # 'fb1@jakcom.com',
            'fb2@jakcom.com',
            # 'fb3@jakcom.com',
            # 'tx@jakcom.com',
        ]
        for account in account_list:
            url = 'https://fb.alibaba.com/reactive/modules?'
            public = Public(account)
            params = {
                '_tb_token_': public.tb_token,
                'protocol': {
                    "api":"reviewManager",
                    "modules":[
                        {
                            "name":"interplay.reviewmananger.tab.reviewcount",
                            "param":{
                                "selectedTab":"reviewed"
                            }
                        },
                        {
                            "name":"interplay.reviewmananger.review.list",
                             "param":{
                                 "currentPage":1,
                                 "pageSize":5,
                                 "selectedTab":"reviewed"
                             }
                         },
                        {
                            "name":"interplay.reviewmananger.review.pagination",
                            "param":{
                                "selectedTab":"reviewed",
                                "currentPage":1,
                                "pageSize":5
                            }
                        }
                    ],
                    "version":"1.0","param":{
                        "selectedTab":"reviewed"
                    },
                    "streamId":2,
                    "timestamp":1561692729707,
                    "timeout":"3000"
                }
            }
            headers = public.headers
            # headers['accept'] = 'application/json'
            headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                callback=self.get_page,
                headers=headers,
                meta={
                    'public': public,
                },
                dont_filter=True
            )

    def get_page(self, response):
        print(dir(response))
        print(response.text)
        tree = json.loads(response.body)
        print(tree)