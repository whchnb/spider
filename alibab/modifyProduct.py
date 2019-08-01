# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: modifyProduct.py
@time: 2019/7/1 12:52
@desc:  在线产品修改
"""
import re
import json
import requests
from alibaba.public import Public


class ModifyProduct(Public):
    def __init__(self, account, itemId, sku):
        self.account = account
        self.itemId = itemId
        self.sku = sku
        super(ModifyProduct, self).__init__(self.account)

    def getData(self):
        codeDict = {}
        multipleDict = {}
        url = 'https://post.alibaba.com/product/publish.htm?itemId=' + self.itemId
        response = requests.get(url, headers=self.headers)
        catid = re.findall(re.compile(r'cbuCatProp&catId=(\d*?)"'), response.text)[0]
        print(catid)
        responseData = json.loads(re.findall(re.compile(r'window.Json = (.*?);\n', re.S), response.text)[0])
        xsrfToken = re.findall(re.compile(r"tokenValue: '(.*?)'", re.S), response.text)[0]
        codeDatas = responseData['components']['icbuCatProp']['props']['dataSource']
        self.cookie += '; XSRF-TOKEN=%s' % xsrfToken
        for codeData in codeDatas:
            # print(codeData)
            codeDict[codeData['name']] = codeData['label']
            if codeData.get('dataSource', None) is not None:
                codeMultipleDict = {}
                for multipleData in codeData['dataSource']:
                    codeMultipleDict[multipleData['text']] = multipleData['value']
                multipleDict[codeData['name']] = codeMultipleDict
        # print(codeDict)
        # print('**' * 50)
        # print(multipleDict)
        # print('**' * 50)
        # print(re.findall(re.compile(r'window.Json = (.*?);\n', re.S), response.text)[0])
        locale = responseData['components']['productQuality']['props']['icmp']['global']['locale']
        catId = catid
        totalPage = responseData['components']['productQuality']['props']['icmp']['global']['totalPage']
        currentPage = responseData['components']['productQuality']['props']['icmp']['global']['currentPage']
        riskCheck = responseData['components']['productQuality']['props']['icmp']['global']['riskCheck']
        initAction = responseData['components']['productQuality']['props']['icmp']['global']['initAction']
        userId = responseData['components']['productQuality']['props']['icmp']['global']['userId']
        staticText = responseData['components']['staticText']['props']['value']
        productPropText = responseData['components']['productPropText']['props']['value']
        productCertificateText = responseData['components']['productCertificateText']['props']['value']
        # 标题
        productTitle = responseData['models']['formValues']['productTitle'].replace('+', ' ')
        # 关键词
        productKeywords = responseData['models']['formValues']['productKeywords']
        # 分组
        productGroup = responseData['models']['formValues']['productGroup']
        # 基本信息
        icbuCatProp = responseData['models']['formValues']['icbuCatProp']
        # 产品规格
        saleProp = responseData['models']['formValues']['saleProp']
        # 交易信息 --->  产品数量
        skuList = responseData['models']['formValues']['sku']
        # 产品描述6张图片 1张主图 5张描述图
        scImages = responseData['models']['formValues']['scImages']
        # 产品视频 主图视频 1个详情视频
        imageVideo = responseData['models']['formValues']['imageVideo']
        # 产品视频 详情视频
        detailVideo = responseData['models']['formValues']['detailVideo']
        # ???
        dimensionType = responseData['models']['formValues']['dimensionType']
        # 商品外包装尺寸
        pkgMeasure = responseData['models']['formValues']['pkgMeasure']
        # 毛重
        pkgWeight = responseData['models']['formValues']['pkgWeight']
        # 包装方式
        wholeSalePkgDesc = responseData['models']['formValues']['wholeSalePkgDesc']
        # 包装图片 list
        pkgImageUpload = responseData['models']['formValues']['pkgImageUpload']
        # 发货期
        ladderPeriod = responseData['models']['formValues']['ladderPeriod']
        # 视频模板
        shippingTemplateId = responseData['models']['formValues']['shippingTemplateId']
        # 计量单位
        priceUnit = responseData['models']['formValues']['priceUnit']
        # 发货运费参考
        logisticsCosts = responseData['models']['formValues']['logisticsCosts']
        # 定制包装
        customizedServices = responseData['models']['formValues']['customizedServices']
        # 阶梯价
        ladderPrice = responseData['models']['formValues']['ladderPrice']
        # 自定义属性
        customMoreProperty = responseData['models']['formValues']['customMoreProperty']
        # 定制服务
        productLightCustom = responseData['models']['formValues']['productLightCustom']
        # ???
        market = responseData['models']['formValues']['market']
        #  销售方式
        saleType = responseData['models']['formValues']['saleType']
        # ???
        marketPrice = responseData['models']['formValues']['marketPrice']
        # 产品详情描述编辑方式
        productDescType = responseData['models']['formValues']['productDescType']
        # 产品详情描述
        superText = responseData['models']['formValues']['superText']
        # 是否支持样品服务
        marketSample = responseData['models']['formValues']['marketSample']
        # 单次最多索样数量
        marketSamplingQuantity = responseData['models']['formValues']['marketSamplingQuantity']
        # 样品单价
        marketSamplingPrice = responseData['models']['formValues']['marketSamplingPrice']
        # 样品包描述
        marketSamplingDescription = responseData['models']['formValues']['marketSamplingDescription']
        # 出口信息
        postExport = responseData['models']['formValues']['postExport']
        '''
        # locale
        # catId
        totalPage
        riskCheck
        initAction
        currentPage
        userId
        staticText
        productPropText
        productCertificateText
        '''
        # 私域品服务
        productVisible = responseData['models']['formValues']['productVisible']
        # 电商一站式服务
        ecIntegration = responseData['models']['formValues']['ecIntegration']
        # 仓库类型
        warehouseType = responseData['models']['formValues']['warehouseType']
        # 63705
        postData = {
            'locale': locale,
            'catId': catId,
            'totalPage': totalPage,
            'currentPage': currentPage,
            'riskCheck': riskCheck,
            'initAction': initAction,
            'userId': userId,
            'productTitle': productTitle,
            'productKeywords': productKeywords,
            'productGroup': productGroup,
            'icbuCatProp': icbuCatProp,
            'saleProp': saleProp,
            'sku': skuList,
            'scImages': scImages,
            'imageVideo': imageVideo,
            'detailVideo': detailVideo,
            'dimensionType': dimensionType,
            'pkgMeasure': pkgMeasure,
            'pkgWeight': pkgWeight,
            'wholeSalePkgDesc': wholeSalePkgDesc,
            'pkgImageUpload': pkgImageUpload,
            'ladderPeriod': ladderPeriod,
            'shippingTemplateId': shippingTemplateId,
            'priceUnit': priceUnit,
            'logisticsCosts': logisticsCosts,
            'customizedServices': customizedServices,
            'ladderPrice': ladderPrice,
            'customMoreProperty': customMoreProperty,
            'productLightCustom': productLightCustom,
            'market': market,
            'saleType': saleType,
            'marketPrice': marketPrice,
            'productDescType': productDescType,
            'superText': superText,
            'marketSample': marketSample,
            'marketSamplingQuantity': marketSamplingQuantity,
            'marketSamplingPrice': marketSamplingPrice,
            'marketSamplingDescription': marketSamplingDescription,
            'productVisible': productVisible,
            'ecIntegration': ecIntegration,
            'warehouseType': warehouseType,
            'staticText': staticText,
            'productPropText': productPropText,
            'productCertificateText': productCertificateText,
        }
        return catId, xsrfToken, postData

        # # 提交表单
        # formValues = responseData['models']['formValues']
        # for i in {'logisticsGeneralText', 'customerGroup', 'postExport', 'expressText',
        #           'exportAgreement', 'scPrice', 'fob', 'supply', 'marketMinOrderQuantity'}:
        #     del formValues[i]

    def main(self):
        url = 'https://post.alibaba.com/product/submit.json?step=step3'
        catId, xsrfToken, jsonBody = self.getData()
        # print(catId)
        # print(xsrfToken)
        # print(jsonBody)
        data = {
            'catId': catId,
            'itemId': int(self.itemId),
            'jsonBody': json.dumps(jsonBody)
        }
        headers = {
            'authority': 'post.alibaba.com',
            'method': 'POST',
            'path': '/product/asyncOpt.htm?optType=productPreview',
            'scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': self.cookie,
            'origin': 'https://post.alibaba.com',
            'referer': 'https://post.alibaba.com/product/publish.htm?itemId=' + self.itemId,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'x-xsrf-token': xsrfToken
        }
        response = requests.post(url, headers=headers, data=data)
        # print(response)
        # print(response.text)


def main():
    # itemId = '62186071989'
    # itemId = '62187007939'
    itemId = '62194454912'
    sku = 'CC2'
    account = 'fb3@jakcom.com'
    modifyProduct = ModifyProduct(account, itemId, sku)
    modifyProduct.main()
    # print(modifyProduct.cookie)


if __name__ == '__main__':
    main()
