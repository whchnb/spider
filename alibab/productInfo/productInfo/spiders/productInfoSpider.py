# -*- coding: utf-8 -*-
import json
import scrapy
from urllib.parse import urlencode
from alibaba.productInfo.productInfo.items import ProductinfoItem
from alibaba.productInfo.productInfo.public import Public


class ProductinfospiderSpider(scrapy.Spider):
    name = 'productInfoSpider'
    allowed_domains = ['hz-productposting.alibaba.com']
    start_urls = ['http://hz-productposting.alibaba.com/']

    # 重写 start_requests
    def start_requests(self):
        account_list = [
            # 'fb1@jakcom.com',
            # 'fb2@jakcom.com',
            'fb3@jakcom.com',
            # 'tx@jakcom.com',
        ]
        for account in account_list:
            url = 'https://hz-productposting.alibaba.com/product/group_ajax.do?'
            public = Public(account)
            csrfToken = public.get_csrf_token()
            params = {
                'event': 'listGroupCombine',
                'ctoken': public.ctoken,
                '_csrf_token_': csrfToken,
            }
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                callback=self.getGroupId,
                headers=public.headers,
                meta={
                    'public': public,
                    'csrfToken': public.csrfToken
                },
                dont_filter=True
            )

    def getGroupId(self, response):
        public = response.meta['public']
        datas = json.loads(response.text)['data']
        for data in datas:
            url = 'https://hz-productposting.alibaba.com/product/managementproducts/asyQueryProductsList.do?'
            params = {
                'statisticsType': 'month',
                'repositoryType': 'all',
                'imageType': 'all',
                'groupId': data['id'],
                'groupLevel': 1,
                'showType': 'onlyMarket',
                'status': 'all',
                'page': 1,
                'size': 10,
                'ctoken': public.ctoken,
                '_csrf_token_': public.csrfToken,
            }
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                callback=self.get_page,
                headers=public.headers,
                meta={
                    'public': public,
                    'groupId': data['id'],
                },
                dont_filter=True
            )

    def get_page(self, response):
        public = response.meta['public']
        groupId = response.meta['groupId']
        datas = json.loads(response.text)
        counts = datas['count']
        pages = int(counts) // 50 if int(counts) % 50 == 0 else int(counts) // 50 + 1
        for page in range(1, int(pages) + 1):
        # for page in range(1, 2):
            url = 'https://hz-productposting.alibaba.com/product/managementproducts/asyQueryProductsList.do?'
            params = {
                'statisticsType': 'month',
                'repositoryType': 'all',
                'imageType': 'all',
                'groupId': groupId,
                'groupLevel': 1,
                'showType': 'onlyMarket',
                'status': 'all',
                'page': page,
                'size': 10,
                'ctoken': public.ctoken,
                '_csrf_token_': public.csrfToken,
            }
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                callback=self.get_data_list,
                headers=public.headers,
                meta={
                    'public': public
                },
                dont_filter=True
            )

    def get_data_list(self, response):
        public = response.meta['public']
        datas = json.loads(response.text)['products']
        for data in datas:
            item = ProductinfoItem()
            item['account'] = public.account
            item['categoryId'] = data['categoryId']
            item['productThumbnail'] = data['absSummImageUrl']  # 缩略图
            item['productTitle'] = data['subject']  # 产品标题
            item['minPrice'] = data['skuMinPrice']  # 最低价
            item['maxPrice'] = data['skuMaxPrice']  # 最高价
            item['priceUnit'] = data['priceUnit']  # 价格单位
            item['principal'] = data['ownerMemberName']  # 负责人
            item['updateDate'] = data['gmtModified']  # 更新时间
            item['productDetailUrl'] = data['productDetailUrl']  # 商品详情链接
            item['finalScore'] = float(data['finalScore'])  # 产品得分
            if item['finalScore'] >= 4:
                item['productLevel'] = '精品'
            elif item['finalScore'] >= 3.5 and item['finalScore'] < 4:
                item['productLevel'] = '普通产品'
            else:
                item['productLevel'] = '劣质产品'
            item['productStatus'] = '审核通过' if data['status'][0] == 'approved' else '审核未通过'  # 产品状态
            item['showNum'] = data['showNum']  # 月曝光量
            item['clickNum'] = data['clickNum']  # 月点击量
            item['fbNum'] = data['fbNum']  # 月反馈量
            item['redModel'] = data['redModel']  # 型号
            item['groupName'] = ','.join([data['groupName1'], data['groupName2'], data['groupName3']])  # 分组
            item['productId'] = data['id']  # 产品id
            print(data['id'])
            # if len(data['exportProducts']) != 0:
            #     item['exportDate'] = data['exportProducts'][0]['gmtModified']  # 出口时间
            #     item['exportRebateRate'] = data['exportProducts'][0]['exportRebateRate']  # 出口回扣率
            #     item['exportId'] = data['exportProducts'][0]['id']  # 出口id
            #     item['exportModel'] = data['exportProducts'][0]['model']  # 出口型号
            #     item['exportName'] = data['exportProducts'][0]['name']  # 出口名称
            #     item['exportStatus'] = data['exportProducts'][0]['stateDesc']  # 出口状态
            #     item['exportServiceName'] = data['exportProducts'][0]['serviceName']  # 产品服务类型
            # item['productKeyWords'] = data['keywords']  # 关键词
            # if data['option'] is not None:
            #     item['productPublishUrl'] = data['option']['copyToNewProduct']  # 产品审核链接
            #     item['productModifyUrl'] = data['option']['editUrl']  # 产品修改链接
            # yield item