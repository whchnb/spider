# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: releaseNewProduct.py
@time: 2019/6/28 15:46
@desc:
"""
import requests
from alibaba.public import Public

class ReleaseNewProduct(Public):
    def __init__(self, account):
        self.account = account
        super(ReleaseNewProduct, self).__init__(self.account)
        self.ctoken = self.get_ctoken()

    def getGroup(self, groupType):
        url = 'https://post.alibaba.com/posting-proxy/product/catenew/AjaxPostCategoryNew.htm'
        params = {
            'language': 'en_us',
            'wholesale': '',
            'ctoken': self.ctoken
        }
        response = requests.get(url, headers=self.headers, params=params)
        groupDatas = response.json()['data']['Recentategories']
        groupDict = {}
        for groupData in groupDatas:
            groupDict[groupData['enName']] = groupData['catId']
            groupDict[groupData['cnName']] = groupData['catId']
        print(groupDict)
        return groupDict[groupType]

    def getProductGroups(self):
        pass


    def earPhones(self, groupCatId):
        pass


    def chooseCategory(self, groupId):
        pass

    def main(self):
        groupType = '消费电子>>耳塞和耳机>>耳塞和耳机'
        groupCatId = self.getGroup(groupType)
        productName = 'PRODUCT_NAME_TEXT'
        productKeywords = 'PRODUCT_KEYWORDS_TEXT'


''
def main():
    accuount = 'fb3@jakcom.com'
    releaseNewProduct = ReleaseNewProduct(accuount)
    releaseNewProduct.main()


if __name__ == '__main__':
    main()