# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: activity.py
@time: 2019/7/22 21:03
@desc: 平台报名活动
"""
import re
import sys
import requests
from dhgate.public import Public, Main


class Activity(Public):
    def __init__(self, account):
        self.account = account
        super(Activity, self).__init__(self.account)

    # 获取sellerid
    def getSellerId(self):
        sellerId = re.findall(re.compile(r'supplierid=(.*?);'), self.cookie)[0]
        return sellerId

    # 获取活动数据
    def getActivityDatas(self, page=1):
        url = 'http://seller.dhgate.com/promoweb/platformacty/actylist.do'
        data = {
            'page': page,
            'actyoption': 0
        }
        response = requests.post(url, headers=self.headers, data=data)
        totalPage = re.findall(re.compile(r"<a href=\"javascript:turnpage\((\d*?),'actyform','0'\)\">\d*?</a>", re.S), response.text)[-1]
        activityDatas = re.findall(re.compile(r'<div class="activity-list">(.*?)</div>\s*</div>', re.S), response.text)
        for activityData in activityDatas:
            try:
                self.activityName = re.findall(re.compile(r'<h2>(.*?)</h2>', re.S), activityData)[0]
                print(self.activityName)
                self.activityType = re.findall(re.compile(r'<div class="activity-detail">[\w\W]*?<dd>(.*?)\s*?</dd>', re.S), activityData)[0]
                self.activityDescription = re.findall(re.compile(r'<dl class="activity-requirement">[\w\W]*?<dd>(.*?)\s*?</dd>', re.S), activityData)[0]
                times = re.findall(re.compile(r'<span class="activity-time">(.*?)</span>', re.S), activityData)
                self.activityTime, self.signUpTime = times
                detailUrlParams = re.findall(re.compile(r'<a href="/promoweb/platformacty/actydetail.do\?(.*?)"', re.S), activityData)[0]
                detailUrl = 'http://seller.dhgate.com/promoweb/platformacty/actydetail.do?' + detailUrlParams
                status, promoId = self.getDetail(detailUrl)
                if status is False:
                    continue
                print(self.activityName)
                print(self.activityType)
                print(self.activityDescription)
                print(self.activityTime)
                print(self.signUpTime)
                productIdsList = status
                self.createActivity(productIdsList, promoId)
            except Exception as e:
                print(e)
                continue
        page += 1
        if page != int(totalPage):
            return self.getActivityDatas(page)


    # 获取活动数据
    def getDetail(self, url):
        response = requests.get(url, headers=self.headers)
        self.targetCustomers = re.findall(re.compile(r'<dt>目标客户：</dt>\s*<dd>\s*(.*?)\s*</dd>', re.S), response.text)
        activityUrl = re.findall(re.compile(r'<a conduct="enroll" href="(.*?)"', re.S), response.text)[0]
        promid = activityUrl.split('=')[1]
        status = self.getActivityDetail(promid)
        return status, promid

    # 获取活动详情数据
    def getActivityDetail(self, promid):
        url = 'http://seller.dhgate.com/promoweb/platformacty/choosepro.do'
        params = {
            'promid': promid
        }
        # response = requests.post(url, headers=self.headers, data=params)
        response = requests.get(url, headers=self.headers, params=params)
        self.totalCounts = re.findall(re.compile(r'id="anotherNumberBox">(\d*?)</b>', re.S), response.text)[0]
        if int(self.totalCounts) == 0:
            return False
        print(self.totalCounts)
        discountRate = re.findall(re.compile(r"全站:<b class='prompt-letter'>(.*?)</b>.*?APP专享:<b class='prompt-letter'>(.*?)</b>", re.S), response.text)
        pcDiscountRate, appDiscountRate = discountRate[0]
        self.pcDiscountMaxRate = pcDiscountRate.split('-')[1]
        self.appDiscountMaxRate = appDiscountRate.split('-')[1]
        print(self.pcDiscountMaxRate)
        print(self.appDiscountMaxRate)
        if float(self.pcDiscountMaxRate) < 7 or float(self.appDiscountMaxRate) < 7:
            return False
        totalProductCounts = re.findall(re.compile(r'id="allProductNumber" value="(\d*?)"', re.S), response.text)[0]
        totalPage = int(totalProductCounts) // 30 if int(totalProductCounts) % 30 == 0 else int(totalProductCounts) // 30 + 1
        productIdList = self.getProductIds(promid, totalPage)
        productIdsList = self.addProductIds(productIdList)
        return productIdsList

    # 获取在线产品数据
    def getProductIds(self, promid, totalPage, page=1, productIdList=[]):
        if page <= totalPage:
            url = 'http://seller.dhgate.com/promoweb/platformacty/nextpageofchoose.do'
            data = {
                'page': page,
                'promid': promid,
                'isblank': True
            }
            response = requests.post(url, headers=self.headers, data=data)
            productIds = re.findall(re.compile(r"<td class='col4'>(.*?)</td>", re.S), response.text)
            productIdList.extend(productIds)
            page += 1
            return self.getProductIds(promid, totalPage, page, productIdList)
        else:
            return productIdList

    # 添加可用商品
    def addProductIds(self, productIdList):
        print('可用产品数', len(productIdList))
        self.productIdList = productIdList
        url = 'http://cs1.jakcom.it/dhgate_promotion/promotion_activity_productlist'
        data = {
            'account': self.account,
            'topcount': self.totalCounts,
            'productids':  ','.join(productIdList)
        }
        response = requests.post(url, data=data)
        productIdsList = [i['productId'] for i in response.json()]
        print('使用的产品数', len(productIdsList))
        return productIdsList

    # 创建活动
    def createActivity(self, productIdsList, promoId):
        data = [
            ('searchtype', '0'),
            ('searchval', ''),
            ('vip', ''),
            ('prodgroup', ''),
            ('page', '1'),
        ]
        for itemcode in productIdsList:
            itemcodes = ('itemcodes', itemcode)
            data.append(itemcodes)
        url = 'http://seller.dhgate.com/promoweb/platformacty/savechoose.do?promid=' + promoId
        print(data)
        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        self.commit(promoId, productIdsList)

    # 获取类目id
    def getCatid(self, promoId):
        url = 'http://seller.dhgate.com/promoweb/platformacty/discount.do?promid=' + promoId
        response = requests.get(url, headers=self.headers)
        catIds = re.findall(re.compile(r'<dl rel="(\d*?)" class="app-allnetwork-wrap">', re.S), response.text)
        return catIds

    # 设置折扣率
    def setDiscountRate(self, promoId, catIds):
        self.pcDiscountMaxRate = 9.5
        self.appDiscountMaxRate = 9
        deliverData = ['%s_%s' % (catId, self.pcDiscountMaxRate) for catId in catIds]
        deliverDataMobile = ['%s_%s' % (catId, self.appDiscountMaxRate) for catId in catIds]
        url = 'http://seller.dhgate.com/promoweb/platformacty/batchdis.do'
        data = {
            'errortip': 'APP专享折扣须高于全站折扣哦！',
            'DeliverData': '|'.join(deliverData),
            'DeliverDataMobile':  '|'.join(deliverDataMobile),
            'promid': promoId,
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)

    # 提交
    def commit(self, promid, productIdList):
        productDiscountData = ['%s-%s-%s' % (i, self.pcDiscountMaxRate, self.appDiscountMaxRate ) for i in productIdList]
        url = 'http://seller.dhgate.com/promoweb/platformacty/commitdis.do'
        data = {
            'DeliverData': ','.join(productDiscountData),
            'promid': promid
        }
        print(data)
        response = requests.post(url, headers=self.headers, data=data)
        print(response)
        print(response.text)
        self.addEmailPhone(promid)

    # 添加邮件电话
    def addEmailPhone(self, promoId):
        sellerId = self.getSellerId()
        url = 'http://seller.dhgate.com/promoweb/platformacty/saverelate.do'
        data = {
            # 'proMerDto.email': 'tx@jakcom.com',
            'proMerDto.email': 'tx@jakcom.com',
            'proMerDto.telephone': '13623627373',
            'proMerDto.promoName': self.activityName,
            'proMerDto.promoId': promoId,
            'proMerDto.sellerId': sellerId
        }
        response = requests.post(url, headers=self.headers, data=data)
        print(response)

    # 日志
    def log(self):
        url = 'http://cs1.jakcom.it/Dhgate_Promotion/promotion_activity_logger'
        data = {
            'account': self.account,
            'activity_name': self.activityName,
            'activity_type': self.activityType,
            'activity_desc': self.activityDescription,
            'time_interval': self.activityTime,
            'time_end': self.signUpTime,
            'target_customer': self.targetCustomers,
            'activity_productcount': len(self.productIdList),
            'activity_productids': ','.join(self.productIdList)
        }


    def main(self):
        self.getActivityDatas()
        self.log()
        # productIdsList = ['430724512', '430599509', '440367478', '438813337', '465972757', '440384450', '475155507', '475166957', '438951265', '446703199', '448986659', '445623313', '452355956', '430632779', '445301164', '454230562', '446690183', '446744631', '441186805', '441180526', '441170340', '437313128', '437167032', '465632578', '440284892', '439595503', '437544226', '435963749', '436828539', '439660061', '436117614', '465852037', '441109367', '433903633', '441066851', '432457497', '439003101', '438406607', '433313555', '477143839', '475332510', '475167113', '475127969', '472269810', '472290681', '472324578', '471843916', '471848020', '471848622', '471853774']
        # promoId = '5942962'
        # # self.createActivity(productIdsList, promoId)
        # catIds = self.getCatid(promoId)
        # self.setDiscountRate(promoId, catIds)



def main():
    m = Main()
    accountList = m.getAcoountPwd()
    for account in accountList[:1]:
        # account = 'k6tech8'
        print('**' * 50)
        print(account)
        print('**' * 50)
        activity = Activity(account)
        activity.main()
        # try:
        #     activity = Activity(account)
        #     activity.main()
        #     m.bug(logName='平台活动', logType='Run', msg='%s 设置成功' % account)
        # except Exception as e:
        #     m.bug(logName='平台活动', logType='Error', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()