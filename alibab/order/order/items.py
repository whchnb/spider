# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OrderItem(scrapy.Item):
    # define the fields for your item here like:
    buyerLoginId = scrapy.Field()   # 会员名
    account = scrapy.Field()    # 账号
    orderId = scrapy.Field()  # 订单号
    buyerName = scrapy.Field()  # 买家姓名
    createTime = scrapy.Field()  # 创建时间
    productTotalAmount = scrapy.Field()  # 总价
    orderStatus = scrapy.Field()  # 订单状态
    fee = scrapy.Field()  # 预估交易服务费
    initialPayment = scrapy.Field()  # 约定总金额
    fundStatus = scrapy.Field()  # 资金状态
    promisedDeliveryDate = scrapy.Field()  # 约定发货时间
    shipmentDate = scrapy.Field()  # 实际发货时间
    shipStatus = scrapy.Field()  # 发货状态
    buyerBusinessIdentity = scrapy.Field()  # 买家商业身份
    buyerAtm = scrapy.Field()  # 买家atm
    buyerCompanyName = scrapy.Field()  # 买家公司
    buyerContactName = scrapy.Field()  # 买家姓名
    createdDate = scrapy.Field()  # 订单创建时间
    buyerEmail = scrapy.Field()  # 买家邮件
    buyerAddress = scrapy.Field()  # 买家地址
    isBuyerPrivacy = scrapy.Field()  # 是否为买方隐私
    bizCode = scrapy.Field()# 商业代码
    shippingMethod = scrapy.Field() # 运输方式
    tradeTerm = scrapy.Field() # 贸易术语
    tradeTermReminder = scrapy.Field()# 贸易术语信息
    shippingFrom = scrapy.Field()# 发货国
    exportServiceText = scrapy.Field() # 出口方式
    address = scrapy.Field() # 收货地址
    estimatedTime = scrapy.Field() # 预计物流时间
    shippingFee = scrapy.Field() # 运费
    remark = scrapy.Field() # 买家备注
    product_datas = scrapy.Field() # 商品信息
    # 若商品未发货，下列字段不会存在   物流和快递
    fieldList = scrapy.Field() # 发货详情
    # 物流模块
    orderType = scrapy.Field() # 物流方式
    platformServiceType = scrapy.Field() # 平台服务类型
    serviceProvider = scrapy.Field() # 承运商
    trackingNumber = scrapy.Field() # 物流单号
    statusName = scrapy.Field() # 物流订单状态
    deliveryTime = scrapy.Field() # 运输时间
    needAudit = scrapy.Field() # 是否需要审计
    abilityOrderId = scrapy.Field() # 订单id
    # 快递模块
    orderNumber = scrapy.Field() # 快递订单号
    logisticsOrderTypeName = scrapy.Field() # 物流服务类型
    stateName = scrapy.Field() # 物流订单状态
    etdTime = scrapy.Field() # 发货时间
    kdneedAudit = scrapy.Field() # 是否需要审计
    kdabilityOrderId = scrapy.Field() # 订单id
    startAdderss = scrapy.Field() # 起运地
    providerName = scrapy.Field() # 服务商

