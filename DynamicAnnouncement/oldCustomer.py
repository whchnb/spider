# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: oldCustomer.py
@time: 2019/5/24 10:45
@desc:  老客维系    每日更新
"""
import json
import requests
from DynamicAnnouncement.public import Public


class OldCustomer(Public):

    def __init__(self):
        super(OldCustomer, self).__init__()

    def get_data(self, queryLifecycle, page=1):
        queryLifecycle_dict = {
            'new': '新客户',
            'active': '活跃客户',
            'lost': '流失客户'
        }
        url = 'https://widget.1688.com/front/getJsonComponent.json'
        queryParam = {
            "queryIdentity": "all",
            "queryGrade": "all",
            "queryLifecycle": queryLifecycle,    # new 新客户 active 活跃客户 lost 流失客户 all 全部客户
            "queryCanInvite": "1",
            "queryBuyerLevel": "all",
            "queryMarketTradeAmount": "all",
            "queryShopTradeAmount": "all",
            "queryShopTradeCount": "all",
            "queryBuyerLoginId": "",
            "pageNum": page,
            "pageSize": 200
        }
        params = {
            'namespace': 'invitationCustomerService',
            'widgetId': 'invitationCustomerService',
            'methodName': 'execute',
            'params': {
                "type": "lost",
                "queryParam": queryParam
            },
            'type': 'lost',
            'queryParam': str(queryParam)
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = json.loads(response.text)['content']['buyerList']
        numbers = len(datas)
        print(numbers)
        if numbers != 0:
            for index, data in enumerate(datas):
                print(index)
                try:
                    ClientID = data['loginId']  # 用户id
                    purchase_level = data['buyerLevel'] # 采购等级
                    lifecycle = queryLifecycle   # 生命周期
                    Authentication_Type = data['identity']  # 身份类型
                    Distribution_channel_level = data.get('gradeName', '-') # 分销渠道等级
                    transaction_amount = data['shopAmount'] # 累计店内交易金额
                    transaction_counts = data['shopCount']  # 累计店内交易次数
                    old_customer = {
                        'ClientID': ClientID,
                        'purchase_level': purchase_level,
                        'lifecycle': queryLifecycle_dict[lifecycle],
                        'Authentication_Type': Authentication_Type,
                        'Distribution_channel_level': Distribution_channel_level,
                        'transaction_amount': transaction_amount,
                        'transaction_counts': transaction_counts,
                    }
                    self.log(old_customer)
                except Exception as e:
                    self.send_test_log(logName='老客维系', logType='Error', msg='生命周期{} 页数{} {}'.format(queryLifecycle, page, str(e)), position='get_data')
            page += 1
            return self.get_data(queryLifecycle, page)
        else:
            return False

    def log(self, data):
        url = 'http://192.168.1.160:90/OSEE_Customer/laokeweixi_save'
        print(data)
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self):
        queryLifecycle_list = [
            'new',
            'active',
            'lost'
        ]
        for queryLifecycle in  queryLifecycle_list:
            print(queryLifecycle)
            try:
                status = self.get_data(queryLifecycle)
                if status is False:
                    self.send_test_log(logName='老客维系', logType='Run', msg='生命周期{} 插入成功'.format(queryLifecycle))
            except Exception as e:
                self.send_test_log(logName='老客维系', logType='Error', msg='生命周期{}'.format(queryLifecycle))


if __name__ == '__main__':
    old = OldCustomer()
    old.main()
