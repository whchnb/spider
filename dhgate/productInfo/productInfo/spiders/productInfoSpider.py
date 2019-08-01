# -*- coding: utf-8 -*-
import re
import json
import scrapy
import requests
from urllib.parse import urlencode
from dhgate.public import Public, Main
from dhgate.productInfo.productInfo.items import ProductinfoItem


class ProductinfospiderSpider(scrapy.Spider):
    name = 'productInfoSpider'
    allowed_domains = ['seller.dhgate.com']
    start_urls = ['http://seller.dhgate.com/']

    def start_requests(self):
        allAccount = Main().getAcoountPwd()
        # allAccount = [
        #         #     'eastfield1',
        #         #     'eastfield2',
        #         #     'eastfield3',
        #         #     'eastfield4',
        #         #     'eastfield5',
        #         #     'eastfield6',
        #         #     'eastfield7',
        #         #     'eastfield8',
        #         #     'eastfield9',
        #         #     'eastfield10',
        #         #     'eastfield3'
        #         # ]
        for account in allAccount:
            # account = 'eastfielddh'
            print('**' * 50)
            print(account)
            print('**' * 50)
            public = Public(account)
            print(public.cookie)
            url = 'http://seller.dhgate.com/prodmanage/shelf/prodShelf.do?dhpath=10001,21001,0202'
            yield scrapy.Request(url, callback=self.getPage, headers=public.headers, dont_filter=True, meta={'public': public})

    def getPage(self, response):
        public = response.meta['public']
        totalCounts = response.xpath('.').re(r'共有(\d*?)条记录')[0]
        pages = int(totalCounts) // 500 if int(totalCounts) % 500 == 0 else int(totalCounts) // 500 + 1
        print(totalCounts)
        for page in range(1, int(pages) + 1):
        # for page in range(1, 2):
            url = 'http://seller.dhgate.com/prodmanage/shelf/prodShelf.do?dhpath=10001,21001,0202'
            data = {
            'vipMessageShow': '1',
            'prodShelfForm.changeProdGroupId': '',
            'prodShelfForm.dispatcheOperation': 'prodShelf',
            'prodShelfForm.hasOperationTip': '0',
            'prodShelfForm.operationTip': '',
            'prodShelfForm.sortType': '0',
            'prodShelfForm.sortField': '',
            'prodShelfForm.isNewVersion': '',
            'prodShelfForm.searchUsedFlag': '',
            'prodShelfForm.isGuidePageShow': '1',
            'prodShelfForm.hasGoldStallAuthority': '',
            'prodShelfForm.databaseAvailable': '3',
            'prodShelfForm.supplierIdentityState': '1',
            'prodShelfForm.isStudentSupplier': '0',
            'prodShelfForm.isMoreSearchConditions': '1',
            'prodShelfForm.productName': '',
            'prodShelfForm.selectedProdGroupId': '',
            'prodShelfForm.itemcode': '',
            'prodShelfForm.skuCode': '',
            'prodShelfForm.skuId': '',
            'prodShelfForm.vaildday': '0',
            'prodShelfForm.isBTypeProd': '',
            'prodShelfForm.operateDateBeginStr': '',
            'prodShelfForm.operateDateEndStr': '',
            'prodShelfForm.onShelfBeginDateStr': '',
            'prodShelfForm.onShelfEndDateStr': '',
            'prodShelfForm.prodSupportPlan': '',
            'prodShelfForm.scoreItem': '0',
            'prodShelfForm.scoreStart': '',
            'prodShelfForm.scoreEnd': '',
            'prodShelfForm.isLastThreeMonth': '1',
            'selectpagesize': '500',
            'page': str(page),
        }
            yield scrapy.FormRequest(
                url=url,
                callback=self.parse,
                formdata=data,
                headers=public.headers,
                dont_filter=True,
                meta={'public': public}
            )

    def parse(self, response):
        public = response.meta['public']
        datas = response.xpath('//tr[@class="j-mouse-hover"]')
        for data in datas:
            item = ProductinfoItem()
            # print(data.extract())
            item['account'] = public.account
            item['productId'] = data.re(r'<span class="lsWrapOne">.*?(\d*?)</span>')[0]
            item['subject'] = data.re(r'<a class="j-multi-trigger click11".*?>\s*(.*?)\s*</a>')[0]
            item['productUrl'] = 'https:' + data.re(r'<a class="j-multi-trigger click11".*?href="(.*?)".*?>')[0]
            item['score'] = data.re(r'<span class="gradeNum"><span>(.*?)</span>')[0]
            item['groupName'] = data.re(r'<span class="groupreline">(.*?)</span>')[0]
            item['ordercount'] = data.re(r'<td class="right">(\d*?)</td>')[0]
            item['validity'] = data.re(r'<td>(.*?)</td>')[0]
            print(item)
            yield item