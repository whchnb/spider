# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: productTemplate.py
@time: 2019/7/22 19:37
@desc: 关联产品模板
"""
import re
import json
import requests
from dhgate.public import Public, Main

class ProductTemplate(Public):
    def __init__(self, account):
        self.account = account
        self.changDict ={}
        super(ProductTemplate, self).__init__(self.account)

    def getProduct(self):
        print('获取需要添加的产品')
        url = 'http://cs1.jakcom.it/dhgate_promotion/product_tempelate'
        params = {
            'account': self.account,
            'topcount': 18
        }
        response =  requests.get(url, params=params)
        self.productIdDict = {i['productId']:i['subject'] for i in response.json()}
        # print(self.productIdDict)
        return list(self.productIdDict.keys())

    def getTemplateDatas(self, productIdList):
        url = 'http://seller.dhgate.com/prodmanage/relModel/relModel.do'
        headers = self.headers
        headers['Referer'] = 'http://seller.dhgate.com'
        response = requests.get(url, headers=headers)
        # print(self.headers)
        # print(response)
        print(response.url)
        # print(response.headers)
        # print(response.text)
        templateDatas = re.findall(re.compile(r'relModelId=(\d*?)"\s*target="_blank">(.{1,10}?)\s*?</a>\s*?</td>', re.S), response.text)
        print('已有的模板', templateDatas)
        alreadyTemplateName = [i[1] for i in templateDatas]
        print(alreadyTemplateName)
        templateNameList = ['关联一', '关联二', '关联三']
        differenceSet = list(set(templateNameList).difference(set(alreadyTemplateName)))
        print('不符合条件的模板', differenceSet)
        removeTemplateDatas = templateDatas[:-len(templateNameList)]
        needTemplateDatas = templateDatas[-len(templateNameList):]
        # print(needTemplateDatas)
        for index, templateData in enumerate(needTemplateDatas):
            relModelId, templateName = templateData
            if templateName in templateNameList:
                self.changeTemplateData(relModelId, templateName, productIdList[index * 6:(index + 1) * 6])
                continue
            print('需要修改的模板', templateData)
            modelName = differenceSet.pop(0)
            self.changeTemplateData(relModelId, modelName, productIdList[index * 6:(index + 1) * 6], change=True)
        for templateData in removeTemplateDatas:
            relModelIds = templateData[0]
            self.removeTemplateData(relModelIds)

    def changeTemplateData(self, relModelId, modelName, productIdList, change=False):
        # productIdList = self.getProduct()
        # productIdList = ['445263277', '477833612', '477833470']
        url = 'http://seller.dhgate.com/prodmanage/relModel/saveRelModel.do'
        data = {
            'relModelId': relModelId,
            'modelName': modelName,
            'itemcodes': ','.join(productIdList)
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response.text)
        if response.json()['code'] == 1:
            if change == True:
                self.changDict[modelName] = relModelId
            self.sendLog(relModelId, modelName, productIdList)

    def removeTemplateData(self, relModelIds):
        url = 'http://seller.dhgate.com/prodmanage/relModel/deleteRelModel.do'
        data = {
            'relModelIds': relModelIds
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)

    def sendChangeLog(self):
        if len(self.changDict) != 0:
            url = 'http://py1.jakcom.it:5000/dhgate/post/promotion/relative_template'
            data = {
                'account': self.account,
                'template_dict': json.dumps(self.changDict, ensure_ascii=False)
            }
            print(data)
            response = requests.post(url, data=data)
            print(response)
            print(response.text)

    def sendLog(self, relModelId, modelName, productIdList):
        url = 'http://cs1.jakcom.it/dhgate_promotion/temp_logger'
        # print(self.productIdDict)
        for productId in productIdList:
            # for modelName, relModelId in self.changDict.items():
            data = {
                'TempID': relModelId,
                'TempName': modelName,
                'Account': self.account,
                'Product_ID': productId,
                'Product_Title': self.productIdDict[productId]
            }
            response = requests.post(url, data=data)
            print(response)
            print(response.text)

    def main(self):
        productIdList = self.getProduct()
        # print(productIdList)
        if len(productIdList) == 0:
            raise IndexError('%s 没有获取到商品' % self.account)
        self.getTemplateDatas(productIdList)
        self.sendChangeLog()
        # print(self.cookie)
        # self.sendLog()

def main():
    m = Main()
    accountList = m.getAcoountPwd()
    # accountList = [
    #     # 'eastfield1', 'eastfield10', 'eastfield2', 'eastfield3', 'eastfield4', 'eastfield5', 'eastfield6', 'eastfield7','eastfield8', 'eastfield9',
    #     # 'jakcom10', 'jakcom2', 'jakcom3', 'jakcom4', 'jakcom5', 'jakcom6', 'jakcom7', 'jakcom8', 'jakcom9', 'jakcomdh',
    #     # 'jikang1', 'jikang10', 'jikang2', 'jikang3', 'jikang4', 'jikang5', 'jikang6', 'jikang7', 'jikang8', 'jikang9',
    #     'k6tech10', 'k6tech3', 'k6tech4', 'k6tech5', 'k6tech6', 'k6tech7', 'k6tech8', 'k6tech9'
    # ]
    print(accountList)
    for account in accountList:
        print('**' * 50)
        'jakcom6, jakcom7, jakcom9, jakcomdh, k6tech1   k6tech10        k6tech4     k6tech3     k6tech5 k6tech6 k6tech7'
        # account = 'jakcomdh'
        print(account)
        print('**' * 50)
        productTemplate = ProductTemplate(account)
        productTemplate.main()
        try:
            productTemplate = ProductTemplate(account)
            productTemplate.main()
            m.bug(logName='关联产品模板', logType='Run', msg='%s 设置成功' % account)
        except Exception as e:
            m.bug(logName='关联产品模板', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()