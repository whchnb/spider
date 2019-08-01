# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: orderEvalaution.py
@time: 2019/6/28 12:50
@desc: 订单评价
"""

import json
import sys
import requests
from urllib.parse import urlencode
from alibaba.public import Public


class OrderEvalaution(Public):
    def __init__(self, account):
        # self.file = open(r'order.json', 'wb')
        self.account = account
        self.star = {
            1: '非常不满意',
            2: '不满意',
            3: '一般',
            4: '满意',
            5: '非常满意',
        }
        super(OrderEvalaution, self).__init__(self.account)

    def getTotalPages(self):
        url = 'https://fb.alibaba.com/reactive/modules?'
        params = {
            '_tb_token_': self.tb_token,
            'protocol': {
                "api": "reviewManager",
                "modules": [
                    {
                        "name": "interplay.reviewmananger.review.pagination",
                        "param": {
                            "selectedTab": "reviewed",
                            "currentPage": 1,
                            "pageSize": 5
                        }
                    }
                ],
                "version": "1.0", "param": {
                    "selectedTab": "reviewed"
                },
            }
        }
        url = url + urlencode(params)
        response = requests.get(url, headers=self.headers)
        print(response.json())
        totalCount = response.json()[0]['payload']['totalCount']
        totalPages = int(totalCount) // 30 if int(totalCount) % 30 == 0 else int(totalCount) // 30 + 1
        return totalPages

    def get_messege(self):
        totalPages = self.getTotalPages()
        for page in range(1, int(totalPages) + 1):
            url = 'https://fb.alibaba.com/reactive/modules?'
            params = {
                '_tb_token_': self.tb_token,
                'protocol': {
                    "api": "reviewManager",
                    "modules": [
                        {
                            "name": "interplay.reviewmananger.review.list",
                            "param": {
                                "currentPage": page,
                                "pageSize": 30,
                                "selectedTab": "reviewed"
                            }
                        }
                    ],
                    "version": "1.0", "param": {
                        "selectedTab": "reviewed"
                    },
                }
            }
            url = url + urlencode(params)
            response = requests.get(url, headers=self.headers)
            datas = response.json()
            # print(len(datas))
            for index, data in enumerate(datas):
                print(page, index , len(datas))
                try:
                    orderId = data['payload']['orderInfo']['orderId']   # 订单号
                    orderUrl = data['payload']['orderInfo']['orderUrl']   # 订单详情链接
                    reviewTime = data['payload']['orderInfo']['reviewTime']   # 更新时间
                    buyerName = data['payload']['orderInfo']['buyerInfo']['name']   # 买家姓名
                    buyerCountry = data['payload']['orderInfo']['buyerInfo']['countryName']   # 买家国家
                    buyerCountryCode = data['payload']['orderInfo']['buyerInfo']['countryCode']   # 买家国家缩写
                    supplierServicesStars = data['payload']['supplerReview']['latitudeScoreList'][0]['score'] # 供应商服务星级
                    supplierServicesDescription = self.star[int(supplierServicesStars)]   # 供应商服务描述
                    shippingTimeStars = data['payload']['supplerReview']['latitudeScoreList'][1]['score'] # 按时发货星级
                    shippingTimeDescription = self.star[int(shippingTimeStars)]   # 按时发货描述
                    orderStars = data['payload']['productReview'][0]['latitudeScore']['score']  # 订单评价星级
                    orderDescription = self.star[int(orderStars)]   # 订单评价描述
                    productId = data['payload']['productReview'][0]['productId']    # 产品id
                    productUrl = data['payload']['productReview'][0].get('productUrl', '已下架')    # 产品链接
                    productTitle = data['payload']['productReview'][0]['productName']    # 产品标题
                    productImageUrl = data['payload']['productReview'][0]['productImageUrl']    # 产品图片
                    reviewId = data['payload']['productReview'][0]['reviewId']    # 评价Id
                    reviewContent = data['payload']['productReview'][0]['reviewContent']    # 评价内容
                    replyName, replyTime, replyContent = '-', '-', '-'
                    if data['payload']['productReview'][0].get('replyName', None) is not None:
                        # print(data['replyContent']['productReview'][0])
                        replyName = data['payload']['productReview'][0]['replyName']    # 回复人
                        replyTime = data['payload']['productReview'][0]['replyTime']    # 回复时间
                        replyContent = data['payload']['productReview'][0]['replyContent']    # 回复内容
                    else:
                        if orderStars == 5:
                            try:
                                replayCommentUrl = 'https:' + data['payload']['productReview'][0]['reviewAction']['data'][
                                    'url'] + '&ctoken=' + self.get_ctoken()
                                postData = {
                                    '_tb_token_': self.tb_token,
                                    'replyComment': 'Very good buyer, thanks for five stars feedback, welcome back again.'
                                }
                                headers = self.headers
                                headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
                                response = requests.post(replayCommentUrl, headers=headers, data=postData)
                                print(response)
                                print(response.text)
                            except:
                                continue


                    saveData = {
                        'account': self.account,
                        'orderId': orderId,
                        'orderUrl': orderUrl,
                        'reviewTime': reviewTime,
                        'buyerName': buyerName,
                        'buyerCountry': buyerCountry,
                        'buyerCountryCode': buyerCountryCode,
                        'supplierServicesStars': supplierServicesStars,
                        'supplierServicesDescription': supplierServicesDescription,
                        'shippingTimeStars': shippingTimeStars,
                        'shippingTimeDescription': shippingTimeDescription,
                        'orderStars': orderStars,
                        'orderDescription': orderDescription,
                        'productId': productId,
                        'productUrl': productUrl,
                        'productTitle': productTitle,
                        'productImageUrl': productImageUrl,
                        'reviewId': reviewId,
                        'reviewContent': reviewContent,
                        'replyName': replyName,
                        'replyTime': replyTime,
                        'replyContent': replyContent,
                    }
                    self.log(saveData)
                except Exception as e:
                    print(e)
                    print(data)
                    # sys.exit()


    def log(self, data):
        url = 'http://cs1.jakcom.it/AlibabaOrderManage/order_evalaution_save'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def saveJson(self, data):
        line = json.dumps(dict(data), ensure_ascii=False) + ',' + "\n"
        # self.file.write(line.encode('utf-8'))

    def main(self):
        self.get_messege()


def main():
    account_list = [
        'fb1@jakcom.com',
        'fb2@jakcom.com',
        'fb3@jakcom.com',
        'tx@jakcom.com',
    ]
    for account in account_list:
        # account = 'fb3@jakcom.com'
        orderEvalaution = OrderEvalaution(account)
        orderEvalaution.main()


if __name__ == '__main__':
    main()