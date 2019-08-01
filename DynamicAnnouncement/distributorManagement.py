# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: distributorManagement.py
@time: 2019/5/24 11:10
@desc:  分销商管理   每天获取，有则更新，无则插入
"""
import json
import datetime
import requests
from DynamicAnnouncement.timeTransfer import transfer
from DynamicAnnouncement.public import Public


class DistributorManagement(Public):

    def __init__(self):
        super(DistributorManagement, self).__init__()

    # 获取要保存的数据
    def get_data(self,startDate, endDate, page):# 26
        url = 'https://channel.1688.com/event/app/fusion_adapter/mbox.htm'
        queryJson = {
            "fxTimeMin": startDate,
            "fxTimeMax": endDate,
            "guestTaobaoScoreMin": "-10",
            "guestTaobaoScoreMax": "20",
            "pageNum": page,
            "pageSize": 200,
            "sort": "desc",
            "sortType": "fx_time",
            "merchantsType": "consign"
        }
        post_data = {
            'queryJson': (queryJson),
            'namespace': 'getChanelRelaltions',
            'widgetId': 'getChanelRelaltions',
            'methodName': 'execute',
            'params': json.dumps({"queryJson": (queryJson)}),
        }
        # 每请求一次页面，更换一次请求头
        headers_cus = Public()
        headers = headers_cus.headers
        response = requests.post(url, data=post_data, headers=headers)
        try:
            datas = json.loads(response.text)['content']['res']['relations']
        except Exception as e:
            # 获取页面失败，则获取下一页
            self.send_test_log(logName='分销商管理', logType='Error', msg='获取页面失败{} {} {}'.format(startDate, page, str(e)))
            page += 1
            return self.get_data(startDate, endDate, page)
        numbers = len(datas)
        print('第{}页，共有数据{}条'.format(page, numbers))
        # 将获取详情保存在本地
        self.save_start_data_to_file(startDate, page, numbers)
        # 如果存在数据
        if numbers != 0:
            for index, data in enumerate(datas):
                print(index)
                try:
                    channelMemberId = data['channelMemberId']
                    ClientID = data['loginId']  # 买家id
                    Sales_count = data['channelProduct1dCount']  # 已代销商品数
                    cooperation_time = transfer(data['consignCreateTime'])  # 开始合作时间
                    cooperation_state = data['consignStatus']  # 合作状态
                    member_source = data['source']  # 会员来源
                    last_deal_time = data['channelLastPayDate'] if data['channelLastPayDate'] is None else transfer(data['channelLastPayDate'])  # 最近交易时间
                    Thy_dealamount = data['channelPayAmount30d']  # 淘货源近30天交易金额
                    Thy_deal_increase = data['channelPayAmount30dRate']  # 淘货源月交易涨幅
                    Thy_purchase_frequency = data['channelPayOrderCount30d']  # 淘货源采购频次
                    taomai_identitytag_gold = data.get('goldSellerIdentity', '-')
                    taomai_identitytag_ying = data.get('activitySellerIdentity', '-')
                    taomai_identitytag = str(taomai_identitytag_gold) + str(taomai_identitytag_ying)# 淘卖身份标签
                    detail = self.get_channelBussinessDetail(channelMemberId, ClientID)
                    taobao_product_proportion = detail[0]  # 淘宝全店商品占比
                    taobao_order_proportion = detail[1]  # 淘宝全店订单占比
                    taomai_level = detail[2]  # 淘卖等级
                    wechat_payamount_30 = data['wgPayAmount30d']  # 微供近30天交易金额
                    wechat_paycount_30 = data['wgOrderCount30d']  # 微供近30天交易笔数
                    wechat_deliver_30 = data['wgFwOfferCount30d']  # 微供近30天转发商品
                    buyer_data = {
                        'ClientID':ClientID,
                        'Sales_count':Sales_count,
                        'cooperation_time':cooperation_time,
                        'cooperation_state':cooperation_state,
                        'member_source':member_source,
                        'last_deal_time':last_deal_time,
                        'Thy_dealamount':Thy_dealamount,
                        'Thy_deal_increase':Thy_deal_increase,
                        'Thy_purchase_frequency':Thy_purchase_frequency,
                        'taomai_identitytag':taomai_identitytag,
                        'taobao_product_proportion':taobao_product_proportion,
                        'taomai_level':taomai_level,
                        'wechat_payamount_30':wechat_payamount_30,
                        'wechat_paycount_30':wechat_paycount_30,
                        'wechat_deliver_30':wechat_deliver_30,
                        'taobao_order_proportion':taobao_order_proportion,
                    }
                    self.log(buyer_data)
                except Exception as e:
                    self.send_test_log(logName='分销商管理', logType='Error', msg="错误页码{} {}".format(page, e), position='get_data')
            # 页数加1
            page += 1
            # 获取下一页
            return self.get_data(startDate, endDate, page)
        else:
            # 如果没有数据，表明这个月的数据获取完毕，返回结束日期作为下次的开始日期
            return endDate

    # 获取分销商详情
    def get_channelBussinessDetail(self, channelMemberId, ClientID):
        url = 'https://channel.1688.com/event/app/fusion_adapter/mbox.htm'
        data = {
            'channelMemberId': channelMemberId,
            'namespace': 'channelBussinessDetail',
            'widgetId': 'channelBussinessDetail',
            'methodName': 'execute',
            'params': json.dumps({"channelMemberId": channelMemberId}),
        }
        response = requests.post(url, data=data, headers=self.headers)
        try:
            datas = json.loads(response.text)['content']
            ITM_CNT_1D_RATE = datas['rate']['ITM_CNT_1D_RATE']
            PAY_MORD_CNT_1M_RATE = datas['rate']['PAY_MORD_CNT_1M_RATE']
            buyerLevel = datas['relationModel']['aliRelationChannelStatModel']['buyerLevel']
            return ITM_CNT_1D_RATE, PAY_MORD_CNT_1M_RATE, buyerLevel
        except Exception as e:
            self.send_test_log(logName='分销商管理', logType='Error', msg="获取分销商详情失败，用户{} {}".format(ClientID, e), position='get_channelBussinessDetail')

    # 日志
    def log(self, data):
        print(data)
        url = 'http://192.168.1.160:90/OSEE_Customer/FenXiaoShangGuanLi_save'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    # 获取起始时间与结束时间
    def custom_start_end_date(self, start_date='2014-10-01'):
        # 当前年
        now_year = datetime.datetime.now().year
        # 当前月
        now_month = datetime.datetime.now().month
        # 开始年
        start_date_year = start_date.split('-')[0]
        # 开始月
        start_date_month = start_date.split('-')[1]
        # 开始日
        start_date_day = start_date.split('-')[2]
        # 如果开始年与当前年相同并且开始月大于当前月，表示会员获取完毕
        if int(start_date_year) == int(now_year) and int(start_date_month) == int(now_month) + 1:
            return False, False
        # 结束时间
        end_date = datetime.datetime(int(start_date_year), int(start_date_month),
                                     int(start_date_day)) + datetime.timedelta(days=31)
        # 结束年
        end_date_year = end_date.year
        # 结束月
        end_date_month = end_date.month
        # 结束日为1号，构造完整的结束时间
        end_date = '{}-{}-01'.format(end_date_year, end_date_month)
        # 返回开始时间与结束时间
        return start_date, end_date

    # 记录开始时间， 页数， 以及当页的会员数量写入本地文件做记录
    def save_start_data_to_file(self, start_date, page, numbers):
        data = {
            "start_date": start_date,
            "page": page,
            "numbers": numbers
        }
        with open('distributorManagement.json', 'a') as f:
            f.write(json.dumps(data) + '\n')

    def main(self):
        startDate = '2018-5-01'
        while True:
            startDate, endDate = self.custom_start_end_date(startDate)
            print(startDate, endDate)
            if startDate is False:
                break
            else:
                startDate = self.get_data(startDate, endDate, page=1)
                print(startDate)


def main():
    distributorManagement = DistributorManagement()
    distributorManagement.main()


if __name__ == '__main__':
    main()
