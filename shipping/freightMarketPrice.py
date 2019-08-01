# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: freightMarketPrice.py
@time: 2019/6/20 10:29
@desc:
"""
import re
import sys
import time
import datetime
import requests
from w3lib.html import remove_tags
from shipping.cookieSelenium import CookieSelenium
from shipping.IdentificationCodes import IdentificationCodes


class FreightMarketPrice4PX():
    def __init__(self):
        self.cookie = self.get_cookie()
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Cookie': self.cookie,
            'Host': 'order.4px.com',
            'Origin': 'http://order.4px.com',
            'Referer': 'http://order.4px.com/order/finance_management/charge/index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

    def get_cookie(self):
        cookieSelenium = CookieSelenium('http://order.4px.com/order/finance_management/charge/index')
        cookie = cookieSelenium.login_4PX()
        return cookie

    def get_country(self):
        url = 'http://order.4px.com/country/get_for_select'
        response = requests.post(url, headers=self.headers)
        datas = response.json()['data'][1:]
        country_dict = {country['name']: country['code'] for data in datas for country_datas in data['country'] for
                        country in country_datas['countrys']}
        "{'tips': None, 'pinyin': 'ade', 'isHot': 0, 'locale': None, 'pageSize': 0, 'isSelected': 0, 'localeName': '安道尔', 'groupCode': None, 'display': '安道尔(AD)', 'code': 'AD', 'pageNo': 1, 'keyword': None, 'displayRule': None, 'name': '安道尔', 'ename': 'ANDORRA', 'pageNum': 0}"
        # for data in datas:
        #     for country_datas in data['country']:
        #         for country in country_datas['countrys']:
        #             print(country)
        return country_dict

    def get_price(self, country, code, identificationCode):
        print(country, code, identificationCode)
        print(time.time())
        url = 'http://order.4px.com/order/finance_management/charge/query'
        params = {
            'countryName': country,
            'country': code,
            'weight': 1,
            'length': '',
            'width': '',
            'height': '',
            'ogid-pickup': 10,
            'type_value': 'P',
            'verificationCode': identificationCode,
            'ogIdPickup': 10,
            'cargoType': 'P',
            '_search': 'false',
            'rows': 500,
            'page': 1,
            'sidx': '',
            'sord': 'asc',
        }
        response = requests.get(url, params=params, headers=self.headers)
        if '参数不合法' in response.text or '校验码计算结果错误' in response.text:
            return '参数不合法'
        price_datas = response.json()['data']
        print(response.text)
        for price_data in price_datas:
            data = {
                'country': country,  # 国家名称
                'platform': '4PX',  # 物流平台
                'mode_transport': price_data['strPk_name'],  # 运输方式
                'weight': 1,  # 重量
                'cost': price_data['total_amount'],  # 费用合计
                'invalid': price_data['strDeliveryperiod'],  # 时效
                'Trackable': price_data['strTracking'],  # 可跟踪
                'remark': price_data['strOperation'],  # 备注
            }
            print(data)
            send(data)

    def get(self, country, code):
        identificationCodes = IdentificationCodes()
        identificationCode = identificationCodes.identification(
            'http://order.4px.com/base/verification_code/get_image', self.headers, True)
        msg = self.get_price(country, code, identificationCode)
        if msg is not None:
            return self.get(country, code)

    def main(self):
        country_dict = self.get_country()
        for country, code in country_dict.items():
            print(country)
            self.get(country, code)
            # return


class FreightMarketPricePFC():
    def __init__(self):
        self.cookie = self.get_cookie()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'Host': 'www.pfcexpress.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }

    def get_cookie(self):
        cookieSelenium = CookieSelenium('http://www.pfcexpress.com/')
        cookie = cookieSelenium.login_PFC()
        return cookie

    def get_country(self):
        url = 'http://www.pfcexpress.com/Manage/WebManage/Ashx/GetCountry.ashx'
        data = {
            'Flag': 'GetCounrty',
            'Condition': None
        }
        response = requests.post(url, data=data)
        country_dict = {country['CountryId']: (country['CnName'], country['EnName']) for country in
                        response.json()['Counrty']}
        return country_dict

    def get_code(self):
        url = 'http://www.pfcexpress.com/Manage/WebManage/Vip/CustOrderFeeSearch.aspx'
        response = requests.get(url, headers=self.headers)
        VIEWSTATE_re_compile = re.compile(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"',
                                          re.S)
        VIEWSTATEGENERATOR_re_compile = re.compile(
            r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)"', re.S)
        EVENTVALIDATION_re_compile = re.compile(
            r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)"', re.S)
        VIEWSTATE = re.findall(VIEWSTATE_re_compile, response.text)[0]
        VIEWSTATEGENERATOR = re.findall(VIEWSTATEGENERATOR_re_compile, response.text)[0]
        EVENTVALIDATION = re.findall(EVENTVALIDATION_re_compile, response.text)[0]
        return VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION

    def get_price(self, id, country_data, VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION):
        print(country_data)
        url = 'http://www.pfcexpress.com/Manage/WebManage/Vip/CustOrderFeeSearch.aspx'
        postData = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': EVENTVALIDATION,
            'TxtfromCountry': '中国',
            'TargetCountry': '%s(%s)' % (country_data[0], country_data[1]),
            'TxtWeight': '1',
            'TxtLength': '10',
            'TxtWidth': '10',
            'TxtHeight': '10',
            'TxtCurrency': 'RMB',
            'BtnSearch': '运费预算',
            'HiValue': id,
            'HiValue1': '',
            'HiField1': '￥',
            'HiLanWei': '',
            'HiOrder': '',
            'HiFullNames': '',
            'HiCS': '',
            'HiCSS': '',
            'HiStyle': '',
        }
        response = requests.post(url, data=postData, headers=self.headers)
        datas_re_compile = re.compile(
            r'<div class="spn1".*?<img.*?>(.*?)<br />.*?class="spn33".*?>(.*?)</div>.*?class="spn3".*?>(.*?)</div>.*?￥.*?<span.*?>(.*?)</span>.*? <div style="padding: 0 7px;">(.*?)</div>',
            re.S)
        datas = re.findall(datas_re_compile, response.text)
        for data in datas:
            country = country_data[0]
            transport = data[0]
            totalCost = data[3]
            aging = data[1]
            track = data[2]
            remark = [i.strip() for i in remove_tags(data[-1]).strip().split('\n')]
            data = {
                'country': country,  # 国家名称
                'platform': 'PFC',  # 物流平台
                'mode_transport': transport,  # 运输方式
                'weight': 1,  # 重量
                'cost': totalCost,  # 费用合计
                'invalid': aging,  # 时效
                'Trackable': track,  # 可跟踪
                'remark': ''.join(remark),  # 备注
            }
            send(data)
            print(data)

    def main(self):
        country_dict = self.get_country()
        VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION = self.get_code()
        for id, country_data in country_dict.items():
            # print(id,country_data)
            # id = 68
            # country_data = ('捷克', 'Czech Republic')
            self.get_price(id, country_data, VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION)


class FreightMarketPriceSF():
    def __init__(self):
        self.cookie = self.get_cookie()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'Host': 'b2c.sf-express.com',
            'Referer': 'http://b2c.sf-express.com/ruserver/login/login.action',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        self.expressTypeDict = {'39': '国际中东小包平邮', '109': '合同物流蒙邮小包平邮', '98': '测试小包挂号', '24': '国际小包陆运挂号', '110': '合同物流蒙邮小包挂号',
                     '21': '国际芬兰挂号', '36': '国际西邮小包挂号', '102': '合同物流爱邮小包挂号', '0': '通用', '10': '国际小包挂号', '1': '国际标快',
                     '210': '揽收分拣换单', '30': '国际e小包', '54': '国际普货小包挂号', '33': '国际越邮小包平邮', '38': '国际南美小包挂号',
                     '104': '合同物流荷邮小包挂号', '19': '海外仓经济小包平邮', '202': '揽收重货', '201': '揽收特惠', '47': '国际比邮小包平邮',
                     '40': '国际中东小包挂号', '23': '国际小包陆运平邮', '41': '国际台邮小包平邮', '42': '国际台邮小包挂号', '26': '国际经济小包挂号',
                     '9': '国际小包平邮', '203': '揽收零担', '25': '国际经济小包平邮', '99': '测试小包平邮', '63': '国际小包特货平邮', '28': '国际专线小包',
                     '101': '合同物流爱邮小包平邮', '48': '国际比邮小包特惠挂号', '20': '海外仓经济小包挂号', '34': '国际越邮小包挂号', '64': '国际小包特货挂号',
                     '106': '合同物流荷邮小包重挂号', '29': '国际电商专递', '44': '国际卢邮小包挂号', '32': '国际精品小包', '103': '合同物流荷邮小包平邮',
                     '51': 'Wish平邮', '27': '国际专线小包平邮', '35': '国际西邮小包平邮', '211': '揽收分拣不换单'}

    def get_cookie(self):
        cookieSelenium = CookieSelenium('http://b2c.sf-express.com/ruserver/login/login.action')
        cookie = cookieSelenium.login_SF()
        print(cookie)
        return cookie

    def get_country(self):
        url = 'http://b2c.sf-express.com/ruserver/login/loadDestCountry.action'
        response = requests.get(url)
        datas_re_compile = re.compile(r'<li data-value="(.*?)">(.*?)</li>', re.S)
        datas = re.findall(datas_re_compile, response.text)
        country_dict = {i[0]: i[1] for i in datas}
        return country_dict

    def get_price(self, id, country, discount_dict):
        url = 'http://b2c.sf-express.com/ruserver/webuser/calCarigeFeeList.action'
        params = {
            'weight': 1,
            'length': 0,
            'heigth': 0,
            'width': 0,
            'destCountry': id,
        }
        response = requests.post(url, params=params)
        price_dict = {i['ourProduct']: {'carigeFee': i['carigeFee'], 'otherFee': i['otherFee'],
                                        'aging': i['acquisitivePrescription']} for i in response.json()['rows']}
        # print(price_dict)
        datas = response.json()['rows']
        # print(datas)
        # discount = discount_dict[id]
        # print(discount)
        for data in datas:
            # print(data)
            transport = data['ourProduct']
            aging = data['acquisitivePrescription']
            track = True if aging[0].isdigit() else False
            if transport in discount_dict[id].keys():
                discount = discount_dict[id][transport]
                carigeFee = float(data['carigeFee'])    # 运费
                otherFee = float(data['otherFee'])      # 其他费用
                totalCost = carigeFee * discount + otherFee
                postData = {
                    'country': country,  # 国家名称
                    'platform': 'SF',  # 物流平台
                    'mode_transport': transport,  # 运输方式
                    'weight': 1,  # 重量
                    'cost': totalCost,  # 费用合计
                    'invalid': aging,  # 时效
                    'Trackable': track,  # 可跟踪
                    'remark': '-',  # 备注
                }
                send(postData)

    def get_discount(self):
        url = 'http://b2c.sf-express.com/ruserver/webuser/findBaseDiscount.action'
        params = {
            '1': '1',
            'contractStatus': '',
            'validTime': '',
            'expireTime': '',
            'page': '1',
            'rows': '10',
        }
        response = requests.get(url, params=params, headers=self.headers)
        responseDatas = response.json()['rows']
        discount_type_dict = [
            {
                'validTime': i['validTime'].split(' ')[0],
                'expireTime': i['expireTime'].split(' ')[0],
                'id': i['discountId']
            }
            for i in responseDatas
        ]
        for discount in discount_type_dict:
            today = str(datetime.datetime.now().date())
            validTime = discount['validTime']
            expireTime = discount['expireTime']
            print(today, validTime, expireTime)
            if today >= validTime and today <= expireTime:
                url = 'http://b2c.sf-express.com/ruserver/webuser/findCustBaseDetailDiscount.action'
                postData = {
                    'custId': 'jakcom',
                    'validTime': discount['validTime'],
                    'expireTime': discount['expireTime'],
                    'discountStatus': '1',
                    'contractStatus': '1',
                    'departure': '',
                    'destCountry': '',
                    'page': '1',
                    'rows': '500',
                }
                response = requests.post(url, data=postData, headers=self.headers)
                datas =response.json()['rows']
                discount_dict = {}
                for data in datas:
                    if data['destCountry'] not in discount_dict.keys():
                        discount_dict[data['destCountry']] = {
                            self.expressTypeDict[data['expressType']]: data['discount']
                        }
                    else:
                        discount_dict[data['destCountry']][self.expressTypeDict[data['expressType']]] = data['discount']
                return discount_dict
            else:
                continue

    def main(self):
        country_dict = self.get_country()
        discount_dict = self.get_discount()
        for id, country in country_dict.items():
            self.get_price(id, country, discount_dict)
            # return


def send(data):
    # return
    url = 'http://cs1.jakcom.it/purpose/shippingprice_save'
    response = requests.post(url, data=data)
    print(response)
    print(response.text)


def main():
    # freightMarketPrice4PX = FreightMarketPrice4PX()
    # freightMarketPrice4PX.main()

    # freightMarketPricePFC = FreightMarketPricePFC()
    # freightMarketPricePFC.main()

    freightMarketPriceSF = FreightMarketPriceSF()
    freightMarketPriceSF.main()


if __name__ == '__main__':
    main()
