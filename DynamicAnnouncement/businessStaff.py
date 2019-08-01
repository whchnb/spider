# -*- coding: utf-8 -*-
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: businessStaff.py
@time: 2019/5/23 14:58
@desc:生意参谋
"""
import time
import json
import datetime
import requests
from DynamicAnnouncement.timeTransfer import transfer
from DynamicAnnouncement.public import Public


class BusinessStaff(Public):

    def __init__(self):
        super(BusinessStaff, self).__init__()
        # 需要保存的数据
        self.buyer_risk = {}

    def get_customer_data(self):
        # 获取所有客户目标链接
        url = 'https://sycm.1688.com/ms/customer/customerDetail.json'
        # 获取今天的时间
        today = datetime.datetime.now().date()
        # 构造昨天的时间
        yestday = today - datetime.timedelta(days=1)
        # 构造30日之前的时间
        mounth_ago = today - datetime.timedelta(days=30)
        #
        self.get_risk_type(yestday)
        params = {
            'dateRange': '{}|{}'.format(mounth_ago, yestday),
            'dateType': 'recent30',
            'pageSize': '1000',  # 514
            'page': '1',
            'order': 'desc',
            'orderBy': 'payAmount',
            'buyerType': '整体客户',
            '_': str(time.time()).replace('.', '')[:13],
        }
        response = requests.get(url, headers=self.headers, params=params)
        datas = json.loads(response.text)['data']['data']
        numbers = len(datas)
        print(numbers)
        for index, data in enumerate(datas):
            print(index)
            buyerLoginId = data['buyerLoginId'].get('value', '-')
            try:
                buyer_datas = {
                    'purchaselevel': data['buyerCreditLevel'].get('value', '-'),  # 采购等级
                    'businessmodel': data['identityName'].get('value', '-'),  # 业务模式
                    'Area': data['custAreaName'].get('value', '-'),  # 所在地区
                    'firstpaytime': data['firstPayDate'].get('value', '-'),  # 首次支付日期
                    'lastpaytime': data['lastPayDate'].get('value', '-'),  # 末次支付日期
                    'payamount_90': data['payAmtAll'].get('value', '-'),  # 90天累计支付金额
                    'payamount_30': data['payAmount'].get('value', '-'),  # 30天支付金额
                    'payorders_30': data['payParentOrderNum']['value'],  # 30天支付订单数
                    'Company': data['companyName'].get('value', '-'),  # 公司名称
                }
                statDate = data['statDate']['value']
                statDate = transfer(statDate)
                buyerType = self.get_buyer_type(buyerLoginId, statDate)
                buyer_datas['ClientID'] = buyerLoginId  # 卖家id
                buyer_datas['Clienttype'] = buyerType  # 客户类型
                # buyer_datas['statDate'] = statDate  # 更新日期
                buyer_datas['Opportunityrisk_type'] = self.buyer_risk[buyerLoginId][
                    'risk_type'] if buyerLoginId in self.buyer_risk.keys() else '-'  # 机会风险类型
                buyer_datas['payorders_90'] = self.buyer_risk[buyerLoginId][
                    'historyPayOrdCnt'] if buyerLoginId in self.buyer_risk.keys() else '-'  # 90天累计支付订单数
                buyer_datas['cycle_60'] = self.buyer_risk[buyerLoginId][
                    'purchaseCycle'] if buyerLoginId in self.buyer_risk.keys() else '-'  # 60天平均采购周期
                buyer_datas['Days_overdue_purchase'] = self.buyer_risk[buyerLoginId][
                    'exceedTimeNotPurchaseCnt'] if buyerLoginId in self.buyer_risk.keys() else '-'  # 超期未采购天数
                # 写入日志
                print(buyer_datas)
                self.log(buyer_datas)
            except Exception as e:
                self.send_test_log(logName='生意参谋', logType='Error', msg="发送第{} {} 时出错 {}".format(index, buyerLoginId, e))

    # 日志
    def log(self, data):
        # print(data)
        url = 'http://192.168.1.160:90/OSEE_Customer/shenyicanmou_save'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    # 获取客户类型
    def get_buyer_type(self, buyerLoginId, statDate):
        url = 'https://sycm.1688.com/ms/customer/getCustomerBaseInfo.json'
        params = {
            'dateType': 'day',
            'dateRange': '{}|{}'.format(statDate, statDate),
            'buyerLoginId': buyerLoginId.encode('utf-8'),
            '_': str(time.time()).replace('.', '')[:13]
        }
        response = requests.get(url, headers=self.headers, params=params)
        data = json.loads(response.text)['data']
        buyerType = data['buyerType']['value']
        return buyerType

    # 获取机会风险类型个数目
    def get_count_risk(self, statDate):
        # 获取机会风险类型个数目标链接
        url = 'https://sycm.1688.com/ms/customer/getChanceRiskCntForTab.json'
        params = {
            'dateRange': '{}|{}'.format(statDate, statDate),
            'dateType': 'day',
            '_': str(time.time()).replace('.', '')[:13],
        }
        response = requests.get(url, headers=self.headers, params=params)
        data = json.loads(response.text)['data']
        # 获取机会风险类型个数
        risk_lists = [
            {'riskType': 'notPurchase', 'orderBy': 'exceedTimeNotPurchaseCnt', 'value': '超期未采购',
             'count': data['notPurchaseTab']},
            {'riskType': 'purchaseDown', 'orderBy': 'payAmtChangeRateLstMth', 'value': '采购下降明显',
             'count': data['purchaseDownTab']},
            {'riskType': 'loseCustomer', 'orderBy': 'historyPayAmount', 'value': '即将流失客户',
             'count': data['loseCustomerTab']},
            {'riskType': 'newCustomer', 'orderBy': 'buyerCreditLevel', 'value': '实力新客户',
             'count': data['newCustomerTab']},
            {'riskType': 'purchaseUp', 'orderBy': 'payAmtChangeRateLstMth', 'value': '采购增长明显',
             'count': data['purchaseUpTab']},
        ]
        return risk_lists

    # 获取风险的目标链接
    def get_risk_type(self, statDate):
        # 获取风险的目标链接
        url = 'https://sycm.1688.com/ms/customer/chanceRisk.json'
        # 获取机会风险类型的数据
        risk_lists = self.get_count_risk(statDate)
        for risk in risk_lists:
            # 拼接所需要的参数
            params = {
                'dateRange': '{}|{}'.format(statDate, statDate),
                'dateType': 'day',
                'pageSize': risk['count'],
                'page': '1',
                'order': 'desc',
                'orderBy': risk['orderBy'],
                'riskType': risk['riskType'],
                'buyerLevels': '',
                'buyerTypes': '',
                '_': str(time.time()).replace('.', '')[:13],
            }
            response = requests.get(url, headers=self.headers, params=params)
            datas = json.loads(response.text)['data']['data']
            # 遍历获取到的数据
            for data in datas:
                buyerLoginId = data['buyerLoginId']['value']  # 买家id
                try:
                    risk_type = risk['value']  # 机会风险类型
                    historyPayOrdCnt = data['historyPayOrdCnt'].get('value', '-')  # 90天累计支付订单数
                    purchaseCycle = data['purchaseCycle'].get('value', '-')  # 60天平均采购周期
                    exceedTimeNotPurchaseCnt = data['exceedTimeNotPurchaseCnt'].get('value', '-')  # 超期未采购天数
                    self.buyer_risk[buyerLoginId] = {
                        'risk_type': risk_type,
                        'historyPayOrdCnt': historyPayOrdCnt,
                        'purchaseCycle': purchaseCycle,
                        'exceedTimeNotPurchaseCnt': exceedTimeNotPurchaseCnt
                    }
                except Exception as e:
                    self.send_test_log(logName='生意参谋', logType='Error', msg='风险类型{} 买家{} {}'.format(risk, buyerLoginId, str(e)))


if __name__ == '__main__':
    businessStaff = BusinessStaff()
    businessStaff.get_customer_data()

