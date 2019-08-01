# -*- coding: utf-8 -*-
import json
import scrapy
from urllib.parse import urlencode
from alibaba.productAnalysis.productAnalysis.items import ProductanalysisItem
from alibaba.productAnalysis.productAnalysis.public import Public


class ProductanalysisinfospiderSpider(scrapy.Spider):
    name = 'productAnalysisInfoSpider'
    allowed_domains = ['data.alibaba.com', 'hz-mydata.alibaba.com']
    start_urls = ['https://data.alibaba.com/']

    # 重写 start_requests
    def start_requests(self):
        account_list = [
            # 'fb1@jakcom.com',
            # 'fb2@jakcom.com',
            'fb3@jakcom.com',
            # 'tx@jakcom.com',
        ]
        for account in account_list:
            url = 'https://hz-mydata.alibaba.com/self/.json?'
            public = Public(account)
            params = {
                'action': 'CommonAction',
                'iName': 'getVipEffectiveProductsAndStats',
                'isVip': 'true',
                # '0.48870658877987827': '',
                'ctoken': public.ctoken,
                # 'dmtrack_pageid': '3d86e8870b837fe25d15764716b9bd618821b35e94',
            }
            data = {
                'statisticType': 'os',
                'region': 'os',
                'statisticsType': 'week',
                'selected': 0,
                'terminalType': 'total',
                'isMyselfUpgraded': True,
                'orderBy': 'views',
                'orderModel': 'desc',
                'pageSize': 10,
                'pageNO': 1,
            }
            data = urlencode(data)
            headers = public.headers
            headers['accept'] = 'application/json'
            headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                method='POST',
                callback=self.get_page,
                headers=headers,
                body=data,
                meta={
                    'public': public,
                },
                dont_filter=True
            )

    def get_page(self, response):
        public = response.meta['public']
        responseData = json.loads(response.text)
        statistics = responseData['value']['statistics']
        counts = statistics['total']
        pages = int(counts) // 1000 if int(counts) % 1000 == 0 else int(counts) // 1000 + 1
        # for page in range(1, int(pages) + 1):
        for page in range(1, 2):
            url = 'https://hz-mydata.alibaba.com/self/.json?'
            params = {
                'action': 'CommonAction',
                'iName': 'getVipEffectiveProductsAndStats',
                'isVip': 'true',
                'ctoken': public.ctoken,
            }
            data = {
                'statisticType': 'os',
                'region': 'os',
                'statisticsType': 'week',
                'selected': 0,
                'terminalType': 'total',
                'isMyselfUpgraded': True,
                'orderBy': 'views',
                'orderModel': 'desc',
                'pageSize': 1000,
                'pageNO': 1,
            }
            data = urlencode(data)
            headers = public.headers
            headers['accept'] = 'application/json'
            headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                method='POST',
                callback=self.get_json_parse,
                headers=headers,
                body=data,
                meta={
                    'public': public,
                },
                dont_filter=True
            )

    def get_json_parse(self, response):
        public = response.meta['public']
        responseData = json.loads(response.text)
        datas = responseData['value']['products']['data']
        for data in datas[:2]:
            print(data)
            item = ProductanalysisItem()
            item['account'] = public.account
            item['productTitle']= data['subject']  # 产品标题
            item['productImgUrl']= data['imageURL']    # 产品图片
            item['productUrl']= data['detailURL']  # 产品链接
            item['productId']= data['id']  # 产品id
            item['principal']= data['firstName'] + ' ' + data['lastName']  # 负责人
            item['exposureNums']= data['sumProdShowNum']   # 曝光次数
            item['clickNums']= data['sumProdClickNum'] # 点击次数
            item['visitNums']= data['sumProdVisitorCnt'] # 访问人数
            item['collectionNums']= data['fav']    # 收藏人数
            item['inquiryNums']= data['sumProdFbNum']  # 询盘人数
            item['inquiryRate']= data['sumProdFbRate']  # 询盘率
            item['submitOrderNums']= data['crtOrd']    # 提交订单个数
            item['clickRate']= data['sumProdClickRate']    # 点击率
            item['share']= data['share']   # 分享人数
            item['compared']= data['cmp']  # 对比人数
            # item['wordSource']= [('%s 曝光数:%s 点击数:%s' % (i['keyword'], i['views'], i['clicks'])) for i in data['keywordEffect']]    # 词来源
            item['wordSource']= data['keywordEffect']    # 词来源
            yield item