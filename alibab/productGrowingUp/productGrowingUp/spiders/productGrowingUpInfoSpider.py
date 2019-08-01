# -*- coding: utf-8 -*-
import json
import scrapy
import requests
from alibaba.public import Public
from urllib.parse import urlencode
from alibaba.productGrowingUp.productGrowingUp.items import ProductgrowingupItem


class ProductgrowingupinfospiderSpider(scrapy.Spider):
    name = 'productGrowingUpInfoSpider'
    allowed_domains = ['hz-productposting.alibaba.com']
    start_urls = ['http://hz-productposting.alibaba.com/']
    skuUrl = 'http://cs1.jakcom.it/alibaba/skulist'
    response = requests.get(skuUrl)
    skuList = response.json()

    def start_requests(self):
        account_list = [
            # 'fb1@jakcom.com',
            'fb2@jakcom.com',
            'fb3@jakcom.com',
            'tx@jakcom.com',
        ]
        for account in account_list:
            public = Public(account)
            url = 'https://hz-productposting.alibaba.com/product/managementproducts/asyQueryProductsListWithPowerScore.do?ctoken=' + public.get_ctoken()
            headers = public.headers
            headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            for sku in self.skuList:
                for boutiqueTag in [1, 4]:
                    data = {
                        'imageType': 'all',
                        'status': 'approved',
                        'displayStatus': 'on',
                        'uiAdvanceSearch': True,
                        'page': 1,
                        'size': 10,
                        'showPowerScore': True,
                        'productKeyword': sku,
                        'productType': '',
                        'boutiqueTag': boutiqueTag,
                    }
                    yield scrapy.Request(
                        url=url,
                        method='POST',
                        callback=self.get_page,
                        headers=headers,
                        body=urlencode(data),
                        meta={
                            'public': public,
                            'sku': sku,
                            'boutiqueTag': boutiqueTag,
                        },
                        dont_filter=True
                    )

    def get_page(self, response):
        public = response.meta['public']
        sku = response.meta['sku']
        boutiqueTag = response.meta['boutiqueTag']
        responseData = json.loads(response.text)
        counts = responseData['count']
        pages = int(counts) // 50 if int(counts) % 50 == 0 else int(counts) // 50 + 1
        for page in range(1, int(pages) + 1):
        # for page in range(1, 2):
            url = 'https://hz-productposting.alibaba.com/product/managementproducts/asyQueryProductsListWithPowerScore.do?ctoken=' + public.get_ctoken()
            headers = public.headers
            headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            data = {
                'imageType': 'all',
                'status': 'approved',
                'displayStatus': 'on',
                'uiAdvanceSearch': True,
                'page': page,
                'size': 50,
                'showPowerScore': True,
                'productKeyword': sku,
                'productType': '',
                'boutiqueTag': boutiqueTag,
            }
            yield scrapy.Request(
                url=url,
                method='POST',
                callback=self.jsonParse,
                headers=headers,
                body=urlencode(data),
                meta={
                    'public': public,
                    'boutiqueTag': boutiqueTag,
                },
                dont_filter=True
            )

    def jsonParse(self, response):
        public = response.meta['public']
        boutiqueTag = response.meta['boutiqueTag']
        responseData = json.loads(response.text)
        productDatas = responseData['products']
        for productData in productDatas:
            try:
                productId = productData['id']   # 产品id
                growUpScore = productData['powerScoreFeature']['prodPowerScore']
                myProductInfoFinalScore = productData['powerScoreFeature']['contentPowerScore'] # 产品信息得分
                myRTS = productData['powerScoreFeature']['isReadyToShip']   # 是否为RTS
                myNegativeComment = productData['powerScoreFeature']['negativeComment'] # 差评数量
                standardProductInfoFinalScore = productData['powerScoreFeatureTarget']['contentPowerScore']
                standardRTS = productData['powerScoreFeatureTarget']['isReadyToShip']
                standardNegativeComment = productData['powerScoreFeatureTarget']['contentPowerScore']
                contentExpressionStatus = '已达标' if myProductInfoFinalScore >= standardProductInfoFinalScore and myRTS == standardRTS and myNegativeComment <= standardNegativeComment else '待优化'   # 内容表达
                myPurchaseBuyer = productData['powerScoreFeature']['purchaseBuyer'] # 支付买家数
                myNinetyDuvToPurchasePercent = productData['powerScoreFeature']['ninetyDuvToPurchasePercent'] # 访客到支付买家的转化率
                myMultiPurchaseBuyer = productData['powerScoreFeature']['multiPurchaseBuyer'] # 复购买家数
                standardPurchaseBuyer = productData['powerScoreFeature']['purchaseBuyer']
                standardNinetyDuvToPurchasePercent = productData['powerScoreFeature']['ninetyDuvToPurchasePercent']
                standardMultiPurchaseBuyer = productData['powerScoreFeature']['multiPurchaseBuyer']
                effectConversionStatus = '已达标' if myPurchaseBuyer >= standardPurchaseBuyer and myNinetyDuvToPurchasePercent >= standardNinetyDuvToPurchasePercent and myMultiPurchaseBuyer>= standardMultiPurchaseBuyer else '待优化'  # 效果转化
                myDeliveryOnTimePercent = productData['powerScoreFeature']['deliveryOnTimePercent'] # 准时发货率
                standardDeliveryOnTimePercent = productData['powerScoreFeature']['deliveryOnTimePercent']
                serviceStatus = '已达标' if myDeliveryOnTimePercent >= standardDeliveryOnTimePercent else '待优化' # 商品服务
                item = ProductgrowingupItem()
                item['account'] = public.account
                item['grow_type'] = '实力优品' if boutiqueTag == 4 else '潜力商品'
                item['productId'] = productId
                item['grow_score'] = growUpScore
                item['content_state'] = contentExpressionStatus
                item['effect_state'] = effectConversionStatus
                item['service_state'] = serviceStatus
                item['product_score'] = myProductInfoFinalScore
                item['badreview_count'] = myNegativeComment
                item['pay_buyer'] = myPurchaseBuyer
                item['pay_rate'] = myNinetyDuvToPurchasePercent
                item['payagain_buyer'] = myMultiPurchaseBuyer
                item['delivery_ontime_rate'] = myDeliveryOnTimePercent
                yield item
            except Exception as e:
                print('---' * 50)
                print(e)
                print(productData)