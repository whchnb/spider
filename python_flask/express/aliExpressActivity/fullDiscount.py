# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: fullDiscount.py
@time: 2019/6/2 11:25
@desc:  满立减
"""
import re
import json
import string
import datetime
import requests
from aliExpressActivity.public import Public


class FullDiscount(Public):
    def __init__(self, account):
        self.account = account
        super(FullDiscount, self).__init__(self.account)
        self.csrf_token = self.get_csrf_token()

    # 获取全部sku
    def get_all_sku_list(self):
        url = 'http://cs1.jakcom.it/alibaba/skulist'
        response = requests.get(url)
        data = json.loads(response.text)
        return data

    # 获取identityCode
    def get_identityCode(self, url):
        # url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm'
        get_headers = self.headers
        get_response = requests.get(url, headers=get_headers)
        identityCode_re_compile = re.compile(r'<input type="hidden" name="identityCode" value="(.*?)"\s?/>', re.S)
        identityCode = re.findall(identityCode_re_compile, get_response.text)[0]
        return identityCode

    # 发布新活动
    def submit(self, url, price_dict):
        # url = 'https://mypromotion.aliexpress.com/store/fixeddiscount/edit.htm?promId=1309813011'
        # 获取全部sku
        all_sku_list = self.get_all_sku_list()
        # 获取identityCode
        identityCode = self.get_identityCode('https://mypromotion.aliexpress.com/store/fixeddiscount/create.htm')
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        wihch_week = int(today) - int(start_day)
        date = '{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[wihch_week])
        # 遍历每个sku
        for sku in all_sku_list:
            # 通过sku获取需要发布的商品id
            product_url = 'http://cs1.jakcom.it/aliexpress_promotion/upload_productquery?account={}&sku={}'.format(self.account, sku)
            product_response = requests.get(product_url)
            productID_data = json.loads(product_response.text)
            # 若返回的为空，说明此sku不可用
            if len(productID_data) != 0:
                # 标题
                title = '{} Wholesale「{}」'.format(sku, date)
                today_now = datetime.datetime.now().date()
                # 开始时间
                startDate = str(today_now).replace('-', '/') + ' 0:00:00'
                # 结束时间
                endDate = str(today_now + datetime.timedelta(days=7)).replace('-', '/') + ' 23:59:00'
                # 价格
                price = int(float(price_dict['B3']['retail_usd']) * 5)
                # 优惠价格
                price_discount = int(round((float(price_dict['B3']['wholesale_5_usd']) - float(price_dict['B3']['wholesale_30_usd'])) * 5))
                data = {
                    '_csrf_token_': self.csrf_token,
                    'identityCode': identityCode,
                    'action': 'fixed_discount_action',
                    'event_submit_do_save': 'anything',
                    '_fms.f._0.pr': startDate,
                    '_fms.f._0.pro': endDate,
                    '_fms.f._0.pa': 'part',
                    '_fms.f._0.mu': 'N',
                    '_fms.f._0.mul': 'Y',
                    '_fms.f._0.prod': ','.join(productID_data),
                    '_fms.f._0.en': 'N',
                    '_fms.f._0.prom': 'FixedDiscount',
                    '_fms.f._0.p': title,
                    'start-date-time': '0',
                    'type': '',
                    'level': '',
                    '_fms.f._0.f': str(price),
                    '_fms.f._0.d': str(price_discount),
                    '_fms.f._0.fi': '',
                    '_fms.f._0.di': '',
                    '_fms.f._0.fix': '',
                    '_fms.f._0.dis': '',
                    'radio-volume-discount': '',
                    '_fms.f._0.fixe': '',
                    '_fms.f._0.disc': '',
                    '_fms.f._0.fixed': '',
                    '_fms.f._0.disco': '',
                    '_fms.f._0.fixedv': '',
                    '_fms.f._0.discou': '',
                }
                headers = self.headers
                headers['content-type'] = 'application/x-www-form-urlencoded'
                response = requests.post(url, data=data, headers=headers)
                if '没有权限' not in response.text:
                    self.send_test_log(logName='满立减', logType='Error',
                                       msg='{} 自建活动 创建失败'.format(self.account),)
                else:
                    log_data = {
                        'Account': self.account,
                        'Promotion_type': '限时限量折扣',
                        'Channel': '自建活动',
                        'Promotion_Name': title,
                        'Begin_time': startDate,
                        'End_time': endDate,
                        'ProductID': ','.join(productID_data),
                    }
                    self.log(log_data)
                    self.send_test_log(logName='全店铺打折', logType='Run',
                                       msg='{} 自建活动 创建成功'.format(self.account))
            else:
                continue

    # 获取全部价格
    def get_price(self):
        url = 'http://cs1.jakcom.it/alibaba/Get_prices'
        response = requests.get(url)
        datas = json.loads(response.text)
        price_dict = {}
        for data in datas:
            price_dict[data['sku']] = {'retail_usd': data['retail_usd'], 'wholesale_5_usd': data['wholesale_5_usd'], 'wholesale_30_usd':data['wholesale_30_usd']}
        return price_dict

    # 类的主函数
    def main(self):
        # 修改活动链接
        change_url = 'https://mypromotion.aliexpress.com/store/fixeddiscount/edit.htm?promId=1309561154'
        # 发布活动链接
        submit_url = 'https://mypromotion.aliexpress.com/store/fixeddiscount/create.htm'
        # 获取价格
        price_dict = self.get_price()
        # 发布新活动
        self.submit(change_url, price_dict)


# 获取速卖通全部账号
def get_account():
    url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def main():
    account_list = get_account()
    for account in account_list:
        # account = 'fb2@jakcom.com'
        fullDiscount = FullDiscount(account)
        try:
            fullDiscount.main()
        except Exception as e:
            fullDiscount.send_test_log(logName='满立减', logType='Error',
                                     msg='{} 自建活动 满立减出错'.format(account))


if __name__ == '__main__':
    main()
