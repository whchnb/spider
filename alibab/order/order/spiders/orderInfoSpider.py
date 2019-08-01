# -*- coding: utf-8 -*-
import re
import time
import json
import scrapy
import requests
from w3lib.url import urljoin
from urllib.parse import urlencode
from alibaba.order.order.public import Public
from alibaba.order.order.items import OrderItem


class OrderinfospiderSpider(scrapy.Spider):
    name = 'orderInfoSpider'
    allowed_domains = ['biz.alibaba.com']
    start_urls = ['https://biz.alibaba.com/']

    # 重写 start_requests
    def start_requests(self):
        account_list = [
            # 'fb1@jakcom.com',
            # 'fb2@jakcom.com',
            # 'fb3@jakcom.com',
            'tx@jakcom.com',
        ]
        for account in account_list:
            public = Public(account)
            # print(public.cookie)
            url = 'https://biz.alibaba.com/ta/ajax/ajaxListOrders.json?'
            # url = 'https://biz.alibaba.com/ta/ajax/ajaxListOrders.json?list=new&ctoken={}&_tb_token_={}&json=%7B%22role%22%3A%22seller%22%2C%22scene%22%3A%22ta%22%2C%22orderType%22%3A%22all%22%2C%22status%22%3A%22all%22%2C%22tags%22%3A%22all%22%2C%22prefatch%22%3Atrue%7D'.format(public.ctoken, public.tb_token)
            params = {
                'list': 'new',
                'ctoken': public.ctoken,
                '_tb_token_': public.tb_token,
                'json': json.dumps({"role":"seller","scene":"ta","orderType":"all","status":"all","tags":"all","prefatch":True}),
            }
            url = url + urlencode(params)
            # print(url)
            yield scrapy.Request(url=url, callback=self.get_page, headers=public.headers, meta={'public': public},
                                 dont_filter=True)

    def get_page(self, response):
        total = json.loads(response.text)['data']['pagination']['count']
        print(total)
        pages = int(total) // 200 if int(total) % 200 == 0 else int(total) // 200 + 1
        public = response.meta['public']
        # for page in range(1, int(pages) + 1):
        for page in range(1, 2):
            url = 'https://biz.alibaba.com/ta/ajax/ajaxListOrders.json?'
            params = {
                'list': 'new',
                'ctoken': public.ctoken,
                '_tb_token_': public.tb_token,
                'json': json.dumps({"role":"seller","scene":"ta","orderType":"all","sellerTodo":None,"buyerTodo":None,"status":"all","tags":"all","createTimeFrom":None,"createTimeTo":None,"amountFrom":None,"amountTo":None,"operator":None,"countries":[],"keyword":"","pagination":{"count":int(total),"page":page,"limit":200}})
            }
            print(page)
            url = url + urlencode(params)
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=public.headers,
                meta={
                    'public': public
                },
                dont_filter=True
            )

    def parse(self, response):
        public = response.meta['public']
        datas = json.loads(response.text)['data']['orders']
        # id_list = [i['id'] for i in datas]
        inquire_url = 'http://cs1.jakcom.it/AlibabaOrderManage/getstate_byorderid'
        inquire_data = {
            # 'orderids': ','.join(id_list),
            'account': public.account
        }
        inquire_response = requests.get(inquire_url, params=inquire_data, timeout=20)
        orderIdList = inquire_response.json()
        for data in datas:
            print(data)
            try:
                itemData = OrderItem()
                orderId = data['id']
                # if str(orderId) not in orderIdList:
                #     continue
                buyerName = data['buyer']['fullName']
                createTime = data['createTime'] # 创建时间
                productTotalAmount = data['productTotalAmount']  # 总价
                orderStatus = data['statusAction']['status']['displayName'] # 订单状态
                isEvaluation = data['statusAction']['actions'][0]['displayName']
                buyerLoginIdLink = data['buyer']['linkUrl'].split('=')[1].split('&')[0]
                # print('-*' * 50)
                # print(buyerLoginIdLink)
                res = requests.get('https://profile.alibaba.com/profile/my_profile.htm?m=' + buyerLoginIdLink, headers=public.headers)
                # print(res)
                # print(res.text)
                buyerLoginId_re_compile = re.compile(r'<a href="https://(.*?).fm.alibaba.com/company_profile.html"', re.S)
                buyerLoginId = ','.join(re.findall(buyerLoginId_re_compile, res.text))
                print(buyerLoginId)
                # print(buyerLoginId)
                # print('-*' * 50)
                if isEvaluation == '邀请评价':
                    orderStatus += '_邀请评价'
                if isEvaluation == '查看付款链接':
                    orderStatus += '_查看付款链接'
                itemData['account'] = public.account
                itemData['orderId'] = orderId
                itemData['buyerName'] = buyerName
                itemData['createTime'] = createTime
                itemData['productTotalAmount'] = productTotalAmount
                itemData['orderStatus'] = orderStatus
                itemData['buyerLoginId'] = buyerLoginId
                detailUrl = urljoin(response.url, data['statusAction']['detailUrl'])
                yield scrapy.Request(
                    detailUrl,
                    # 'https://biz.alibaba.com/ta/detail.htm?spm=a2756.trade-order-list.0.0.2d7c76e9vbboAZ&orderId=14139579501027862&tracelog=from_orderlist_dropdown',
                    callback=self.detail_parse,
                    headers=public.headers,
                    meta={
                        'public': public,
                        'itemData': itemData
                    },
                    dont_filter=True
                )
            except Exception as e:
                print('ERR\n%s'%str(e), data)

    def close_order_parse(self, response, itemData):
        response_data = response.xpath('.').re(r'data = (.*?);\s*data.location')
        data = json.loads(response_data[0])
        try:
            fee = data['fundPayment']['escrowFee']['amount']  # 预估交易服务费
            initialPayment = data['fundPayment']['shouldPayOrderAmount']['amount']  # 约定总金额
        except:
            fee = data['order']['escrowFee']['amount']
            initialPayment = data['order']['orderAmount']
        shipmentDate = data['order']['closedReason']  # 实际发货时间
        buyerContactName = data['buyerContact']['operatorLoginId']  # 买家名称
        buyerAddressData = data['buyerContact']['shipment']
        buyerAddress = buyerAddressData['address'] + ',' + buyerAddressData['address'] + ',' + buyerAddressData.get(
            'city') + ',' + buyerAddressData.get('province', '-') + ',' + buyerAddressData.get('country', '-')  # 买家地址
        product_datas = data['order']['orderItemList']
        remark = data['order'].get('remark', '-')
        serviceProvider = data['logistic'].get('logisticsServiceName', '-')  # 承运商
        trackingNumber = data['logistic'].get('logisticsNo', '-')  # 订单号码
        itemData['fee'] = fee
        itemData['initialPayment'] = initialPayment
        itemData['shipmentDate'] = shipmentDate
        itemData['buyerContactName'] = buyerContactName
        itemData['buyerAddress'] = buyerAddress
        itemData['product_datas'] = product_datas
        itemData['remark'] = remark
        itemData['trackingNumber'] = trackingNumber
        itemData['serviceProvider'] = serviceProvider
        yield itemData

    def detail_parse(self, response):
        public = response.meta['public']
        itemData = response.meta['itemData']
        response_data = response.xpath('.').re(r'window.VISION_SCHEMA = (.*?);\s*try')
        if len(response_data) != 0:
            try:
                data = json.loads(response_data[0])
            except:
                return
            try:
                try:
                    product_datas = data['data']['contractProduct_1']['fields']['productList']
                except:
                    product_datas = '-'
                fund_1 = data['data'].get('fund_1')
                if fund_1 is not None:
                    fee = fund_1['fields'].get('fee', '-')  # 预估交易服务费
                    initialPayment = fund_1['fields'].get('initialPayment', '-')  # 约定总金额
                    fundStatus = fund_1['fields']['fundStatus']  # 资金状态
                    promisedDeliveryDate = data['data']['shipment_1']['fields'].get('promisedDeliveryDate', '-')  # 约定发货时间
                    shipmentDate = data['data']['shipment_1']['fields']['shipmentDate']  # 实际发货时间
                    shipStatusList = data['data']['shipment_1']['fields']['shipmentStep']
                    shipStatus = [i['name'] for i in shipStatusList if i.get('location', None) == 'cur'][0]  # 发货状态
                    buyerBusinessIdentity = data['data']['contractInfo_1']['fields'].get('buyerBusinessIdentity', '-')  # 买家商业身份
                    buyerAtm = data['data']['contractInfo_1']['fields']['buyerAtm']  # 买家atm
                    buyerCompanyName = data['data']['contractInfo_1']['fields'].get('buyerCompanyName', '-')  # 买家公司
                    buyerContactName = data['data']['contractInfo_1']['fields'].get('buyerContactName', '-')  # 买家姓名
                    createdDate = data['data']['contractInfo_1']['fields']['createdDate']  # 订单创建时间
                    buyerEmail = data['data']['contractInfo_1']['fields'].get('buyerEmail', '-')  # 买家邮件
                    buyerAddress = data['data']['contractInfo_1']['fields'].get('buyerAddress', '-')  # 买家地址
                    isBuyerPrivacy = data['data']['contractInfo_1']['fields']['isBuyerPrivacy']  # 是否为买方隐私
                    bizCode = data['data']['contractInfo_1']['fields']['bizCode']  # 商业代码
                    shippingMethod = data['data']['contractShipment_1']['fields'].get('shippingMethod', '-')  # 运输方式
                    tradeTerm = data['data']['contractShipment_1']['fields'].get('tradeTerm', '-')  # 贸易术语
                    tradeTermReminder = data['data']['contractShipment_1']['fields'].get('tradeTermReminder', '-')  # 贸易术语信息
                    shippingFrom = data['data']['contractShipment_1']['fields'].get('shippingFrom', '-')  # 发货国
                    exportServiceText = data['data']['contractShipment_1']['fields'].get('exportServiceText', '-')  # 出口方式
                    address = data['data']['contractShipment_1']['fields'].get('address', '-')  # 收货地址
                    estimatedTime = data['data']['contractShipment_1']['fields'].get('estimatedTime', '-')  # 预计物流时间
                    shippingFee = data['data']['contractShipment_1']['fields'].get('shippingFee', '-')  # 运费
                    remark = data['data']['contractRemark_1']['fields'].get('content', '-')  # 备注
                    itemData['fee'] = fee
                    itemData['initialPayment'] = initialPayment
                    itemData['initialPayment'] = initialPayment
                    itemData['fundStatus'] = fundStatus
                    itemData['promisedDeliveryDate'] = promisedDeliveryDate
                    itemData['shipmentDate'] = shipmentDate
                    itemData['shipStatus'] = shipStatus
                    itemData['product_datas'] = str(product_datas) if product_datas is not None else '-'
                    itemData['buyerBusinessIdentity'] = buyerBusinessIdentity
                    itemData['buyerAtm'] = buyerAtm
                    itemData['buyerCompanyName'] = buyerCompanyName
                    itemData['buyerContactName'] = buyerContactName
                    itemData['createdDate'] = createdDate
                    itemData['buyerEmail'] = buyerEmail
                    itemData['buyerAddress'] = buyerAddress
                    itemData['isBuyerPrivacy'] = isBuyerPrivacy
                    itemData['bizCode'] = bizCode
                    itemData['shippingMethod'] = shippingMethod
                    itemData['tradeTerm'] = tradeTerm
                    itemData['tradeTermReminder'] = tradeTermReminder
                    itemData['shippingFrom'] = shippingFrom
                    itemData['exportServiceText'] = exportServiceText
                    itemData['address'] = address
                    itemData['estimatedTime'] = estimatedTime
                    itemData['shippingFee'] = shippingFee
                    itemData['remark'] = remark
                    print(shipStatus)
                    if shipStatus != '待发货':
                        order_detail_url = 'https://expressexport.alibaba.com/shipping/delivery/initDetail.json?source=TA&tradeOrderId=%s&ctoken=%s' % (
                            itemData['orderId'], public.ctoken)
                        yield scrapy.Request(
                            order_detail_url,
                            callback=self.order_detail_parse,
                            headers=public.headers,
                            meta={
                                'public': public,
                                'itemData': itemData
                            },
                            dont_filter=True
                        )
                    else:
                        print(itemData)
                        yield itemData
                else:
                    self.close_order_parse(response, itemData)
            except Exception as e:
                print('err\n%s\n'%str(e),  response.url,'\n', response_data, '\n', public.account)
                print('\n', itemData['orderStatus'])
        else:
            self.close_order_parse(response, itemData)

    def order_detail_parse(self, response):
        public = response.meta['public']
        itemData = response.meta['itemData']
        print('* ' * 130)
        print(response.url)
        print('* ' * 130)
        res = json.loads(response.text)['data']
        offlineModule = res['offlineModule']['fields']
        logisticsModule = res['logisticsModule']['fields']
        # 物流模块
        if offlineModule['visible'] is True:
            fieldLists = offlineModule.get('list', [])
            fieldList = []
            for filed in fieldLists:
                filedDict = {}
                orderType = filed['orderType']  # 物流方式
                platformServiceType = filed['platformServiceType']  # 平台服务类型
                serviceProvider = filed['serviceProvider']  # 承运商
                trackingNumber = filed['trackingNumber']  # 物流单号
                statusName = filed['statusName']  # 物流订单状态
                deliveryTime = filed['deliveryTime']  # 运输时间
                needAudit = filed['needAudit']  # 是否需要审计
                abilityOrderId = filed['abilityOrderId']  # 订单id
                filedDict['orderType'] = orderType
                filedDict['platformServiceType'] = platformServiceType
                filedDict['serviceProvider'] = serviceProvider
                filedDict['trackingNumber'] = trackingNumber
                filedDict['statusName'] = statusName
                filedDict['deliveryTime'] = deliveryTime
                filedDict['needAudit'] = needAudit
                filedDict['abilityOrderId'] = abilityOrderId
                fieldList.append(filedDict)
            itemData['fieldList'] = json.dumps(fieldList, ensure_ascii=False)
            # itemData['fieldList'] = fieldList
        # 订单模块
        elif logisticsModule['visible'] is True:
            fieldLists = logisticsModule['list']
            fieldList = []
            for filed in fieldLists:
                filedDict = {}
                orderNumber = filed['orderNumber']  # 订单号
                logisticsOrderTypeName = filed['logisticsOrderTypeName']  # 物流服务类型
                stateName = filed['stateName']  # 物流订单状态
                etdTime = filed.get('etdTime', '-')  # 发货时间
                kdneedAudit = filed['needAudit']  # 是否需要审计
                kdabilityOrderId = filed['abilityOrderId']  # 订单id
                startAdderss = filed['originName'] + '-' + filed['destinationName']  # 起运地
                providerName = filed['providerName']  # 服务商
                filedDict['orderNumber'] = orderNumber
                filedDict['logisticsOrderTypeName'] = logisticsOrderTypeName
                filedDict['stateName'] = stateName
                filedDict['etdTime'] = etdTime
                filedDict['needAudit'] = kdneedAudit
                filedDict['abilityOrderId'] = kdabilityOrderId
                filedDict['startAdderss'] = startAdderss
                filedDict['providerName'] = providerName
                fieldList.append(filedDict)
            itemData['fieldList'] = json.dumps(fieldList, ensure_ascii=False)
            # itemData['fieldList'] = fieldList
        print(itemData)
        yield itemData

# {
#     'fundStatus': 'FULFILLED',
#     'exportServiceType': '非一达通出口',
#     'shipmentDate': '待发货',
#     'product_datas': [
#         {'sku': 'Color:Size 8,Storage Capacity:Other',
#          'productId': '60563233492',
#          'quantity': '1.00',
#          'currentUnitPrice': 'US $19.9000',
#          'link': '//www.alibaba.com/product-detail/Wholesale-Jakcom-R3-Smart-Ring-Consumer_60563233492.html',
#          'unit': 'Pieces',
#          'img': '//sc01.alicdn.com/kf/HTB14g9VKkSWBuNjSszdq6zeSpXaY.jpg',
#          'name': 'Wholesale Jakcom R3 Smart Ring Consumer Electronics Mobile Phones Celular Android Alibaba.Com In Russian Android Smartphone',
#          'storeList': [],
#          'currentProductPrice': 'US $19.90'
#          }
#     ],
#     'promisedDeliveryDate': '2019-06-18之内发货',
#     'fee': 'US $0.40',
#     'productTotalAmount': 19.9,
#     'createTime': '2019-06-17',
#     'initialPayment': 'US $19.90',
#     'buyerName': 'Sukh Dhindsa',
#     'orderId': '14893490001020291',
#     'shipStatus': ['待发货']}
