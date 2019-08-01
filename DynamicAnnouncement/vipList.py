# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: vipList.py
@time: 2019/5/23 20:11
@desc:  会员列表  获取昨天到今天之间新加入的会员
"""
import re
import json
import datetime
import requests
from DynamicAnnouncement.timeTransfer import timeTransfer, transfer
from DynamicAnnouncement.public import Public


class VipList(Public):

    def __init__(self):
        super(VipList, self).__init__()
        self.tb_token = self.get_csrf_token()

    # 获取tb_token
    def get_csrf_token(self):
        token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        token = re.findall(token_re_compile, self.headers['cookie'])[0]
        return token

    # 获取要保存的数据
    def get_data(self, startDate, endDate, page):
        url = 'https://widget.1688.com/front/getJsonComponent.json'
        queryJson = {
            "custTimeMin": timeTransfer(startDate),
            "custTimeMax": timeTransfer(endDate),
            "pageNum": page, "pageSize": 200,
            "sort": "asc",
            "sortType": "customer_time"
        }
        params = {
            'namespace': 'getCustomerRelations',
            'widgetId': 'getCustomerRelations',
            'methodName': 'execute',
            'params': {"queryJson": queryJson},
            'queryJson': str(queryJson),
            '_tb_token_': self.tb_token,
        }
        response = requests.get(url, headers=self.headers, params=params)
        datas = json.loads(response.text)['content']['res']['customerDatas']
        # 获取当页会员数量
        numbers = len(datas)
        print('当前第{}页 共{}条'.format(page, numbers))
        if numbers == 0:
            # 若会员数量为0，说明这个月的会员已经全部获取完毕，返回结束时间，作为下一阶段的开始时间
            return False
        else:
            for index, data in enumerate(datas):
                print(index)
                Jointime = transfer(data['custTime'])  # 加入会员时间
                try:
                    ClientID = data['loginId']  # 买家id
                except:
                    continue
                membership = data.get('guestPurchaseLevel', '-')  # 会员身份
                Taobao_Url = data.get('guestTaobaoShopUrl', '-')  # 店铺地址
                buyer_data = {
                    'Jointime': Jointime,
                    'ClientID': ClientID,
                    'membership': membership,
                    'Taobao_Url': Taobao_Url,
                }
                buyer_detail = self.get_buyer_detail(ClientID)
                if buyer_detail is False:
                    # 如果未获取到详细数据，则进行下一条数据的获取
                    continue
                buyer_detail_data = {**buyer_data, **buyer_detail}
                self.log(buyer_detail_data)
            # 页数加1
            page += 1
            # 继续获取下一页的会员
            return self.get_data(startDate, endDate, page)

    # 获取详细数据
    def get_buyer_detail(self, buyerLoginId):
        url = 'https://widget.1688.com/front/getJsonComponent.json'
        params = {
            'namespace': 'getCustomerDetail',
            'widgetId': 'getCustomerDetail',
            'methodName': 'execute',
            'params': str({"buyerLoginId": buyerLoginId}),
            'buyerLoginId': buyerLoginId,
            '_tb_token_': self.tb_token,
        }
        response = requests.get(url, params=params, headers=self.headers)
        data = json.loads(response.text)['content']
        try:
            # 若发生错误，表示会员名不合法，无法继续获取详细数据
            main_identity = data['result']['result'].get('identity_lv1_name', '暂无')  # 主营身份
        except:
            # 返回False
            return False
        major_business = data['custDetail'].get('identityBus', '暂无') if data['custDetail'].get('identityBus',
                                                                                               '暂无') != '0' else '暂无'  # 主营行业
        business_model = data['custDetail'].get('busModel', '暂无')  # 经营模式
        member_source = data['custDetail']['custSource'] if data['custDetail'].get('custSource',
                                                                                   None) is not None else '暂无'  # 会员来源
        name = data['custDetail'].get('custName', '-')  # 姓名
        mobile = data['custDetail'].get('custMobile', '-')  # 电话
        address = data['custDetail'].get('custAddr', '-')  # 地址
        email = data['custDetail'].get('custEmail', '-')  # 邮箱
        description = data['custDetail'].get('custRemark', '-')  # 备注
        buyer_detail = {
            'main_identity': main_identity,
            'major_business': major_business,
            'business_model': business_model,
            'member_source': member_source,
            'name': name,
            'mobile': mobile,
            'address': address,
            'email': email,
            'description': description
        }
        # 返回构建好的字典
        return buyer_detail

    # 日志
    def log(self, data):
        url = 'http://192.168.1.160:90/OSEE_Customer/huiyuanliebiao_save'
        respnse = requests.post(url, data=data)
        print(respnse)
        print(respnse.text)

    def main(self):
        # 现在的时间
        today = datetime.datetime.now().date()
        # 开始时间
        startDate = str(today - datetime.timedelta(days=1))
        # 结束时间
        endDate = str(today)
        # 状态码， False 表示获取完成
        stautus = self.get_data(startDate, endDate, page=1)
        if stautus is False:
            self.send_test_log(logName='获取昨天今天的会员列表', logType='Run', msg='获取{} {}会员列表成功'.format(startDate, endDate))

def main():
    vip = VipList()
    vip.main()


if __name__ == '__main__':
    main()
