# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: vipList.py
@time: 2019/5/23 20:11
@desc:  从店铺创建之日开始，获取所有的会员
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
        self.save_start_data_to_file(startDate, page, numbers)
        if numbers == 0:
            # 若会员数量为0，说明这个月的会员已经全部获取完毕，返回结束时间，作为下一阶段的开始时间
            return endDate
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

    # 日志
    def log(self, data):
        url = 'http://192.168.1.160:90/OSEE_Customer/huiyuanliebiao_save'
        respnse = requests.post(url, data=data)
        print(respnse)
        print(respnse.text)

    # 记录开始时间， 页数， 以及当页的会员数量写入本地文件做记录
    def save_start_data_to_file(self, start_date, page, numbers):
        data = {
            "start_date": start_date,
            "page": page,
            "numbers": numbers
        }
        with open('vip.json', 'a') as f:
            f.write(json.dumps(data) + '\n')

    def main(self):
        startDate = '2014-10-01'
        while True:
            startDate, endDate = self.custom_start_end_date(startDate)
            print(startDate, endDate)
            if startDate is False:
                break
            else:
                startDate = self.get_data(startDate, endDate, page=1)
                print(startDate)


def main():
    vip = VipList()
    vip.main()


if __name__ == '__main__':
    main()
