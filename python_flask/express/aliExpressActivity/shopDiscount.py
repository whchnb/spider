# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: shopDiscount.py
@time: 2019/6/1 14:28
@desc:  全店铺打折
        1. 自建活动     每周一次
        2. 官方活动     手动触发
@step:  创建营销活动分组
"""
import re
import json
import string
import datetime
import requests
from aliExpressActivity.public import Public


class ShopDiscount(Public):
    def __init__(self, account):
        self.account = account
        super(ShopDiscount, self).__init__(account)
        self.csrf_token = self.get_csrf_token()

    # 获取identityCode
    def get_identityCode(self):
        url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm'
        get_headers = self.headers
        get_response = requests.get(url, headers=get_headers)
        identityCode_re_compile = re.compile(r'<input type="hidden" name="identityCode" value="(.*?)" />', re.S)
        identityCode = re.findall(identityCode_re_compile, get_response.text)[0]
        return identityCode

    # 获取剩余时间，剩余次数以及现有活动
    def get_hours_count(self):
        url = 'https://mypromotion.aliexpress.com/store/storediscount/list.htm'
        response = requests.get(url, headers=self.headers)
        hours_count_re_compile = re.compile(r'月剩余量: 活动数: .*?">(.*?)</.*?">(.*?)</strong> 小时</li>', re.S)
        activity_type_re_compile = re.compile(r'<a class=".*list-operate-create.*?"\s*href="(.*?)"\s*?.*?>(.*?)</a>',
                                              re.S)
        activities = re.findall(activity_type_re_compile, response.text)
        activities_dict = {i[1]: 'https://mypromotion.aliexpress.com' + i[0] for i in activities}
        hours_count = re.findall(hours_count_re_compile, response.text)
        currentHours, currentCount = hours_count[0][0], hours_count[0][1]
        return currentHours, currentCount, activities_dict

    # 添加新的分组id以及构造标题日期
    def add_group(self):
        print('正在创建新的分组')
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        today = datetime.datetime.now().date().strftime("%W")
        start_day = datetime.datetime(year, month, 1).strftime("%W")
        wihch_week = int(today) - int(start_day)
        date = '{}{}{}'.format(year, str(month).zfill(2), string.ascii_uppercase[wihch_week])
        groupName = 'New Products ' + date
        url = 'https://mypromotion.aliexpress.com/store/marketinggroup/ajax/create.htm'
        data = {
            'groupName': groupName
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        response = requests.post(url, headers=headers, data=data)
        gruopId = json.loads(response.text)['groupId']      # 150000753007
        return date, gruopId

    # 获取需要添加的商品id
    def get_product(self):
        print('正在添加商品')
        url = 'http://cs1.jakcom.it/aliexpress_promotion/upload_productquery?account={}'.format(self.account)
        response = requests.get(url)
        datas = json.loads(response.text)
        product_ids = []
        if len(datas) != 0:
            return datas
        else:
            msg = '{} 没有获取到商品'.format(self.account)
            self.send_test_log(logName='全店铺打折', logType='Error', msg=msg)
            return msg

    # 添加商品
    def add_products(self, gruopId):
        # 获取需要添加的商品id
        self.product_ids = self.get_product()
        if type(self.product_ids) is str:
            return self.product_ids
        url = 'https://mypromotion.aliexpress.com/store/marketinggroupproduct/ajax/create.htm'
        data = {
            '_csrf_token_': self.csrf_token,
            'groupId': gruopId,
            'productIds': ','.join(self.product_ids)
        }
        headers = self.headers
        response = requests.post(url, data=data, headers=headers)
        if '没有权限' not in response.text:
            self.send_test_log(logName='全店铺打折', logType='Error',
                               msg='{} {}'.format(self.account, data),
                               position='分组添加商品失败')
            return '{} {} 分组添加商品失败'.format(self.account, data)

    # 获取商铺id
    def get_storeNumber(self, gruopId):
        print(gruopId)
        url = 'https://mypromotion.aliexpress.com/store/marketinggroupproduct/list.htm?groupId={}&page=1000'.format(
            gruopId)
        response = requests.get(url, headers=self.headers)
        store_number_re_compile = re.compile(
            r'<a href="http://www.aliexpress.com/store/(.*?)" target="_blank">进入我的商铺</a>', re.S)
        store_number = re.findall(store_number_re_compile, response.text)[0]
        return store_number

    # 创建新活动
    def create_new_activity(self, url, activity_type):
        # 获取标题日期，创建好的分组id
        date, gruopId = self.add_group()
        # 获取商铺id
        store_number = self.get_storeNumber(gruopId)
        # 在分组中添加商品
        msg = self.add_products(gruopId)
        if msg is not None:
            return msg
        print('正在创建活动')
        title = 'Week Special Offer 「{}」'.format(date)
        # 获取identityCode
        identityCode = self.get_identityCode()
        # 重新获取剩余时间以及剩余次数
        currentHours, currentCount, activities_dict = self.get_hours_count()
        currentCount = int(currentCount)
        currentHours = int(currentHours)
        today = datetime.datetime.now().date()
        # 如果剩余次数大于0并且剩余时间大于168，正常发布
        if currentCount > 0 and currentHours >= 168:
            startDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 0:00:00'
            endDate = str(today + datetime.timedelta(days=8)).replace('-', '/') + ' 23:59:00'
        # 如果剩余次数大于0并且剩余时间小于168，将剩余时间全部发布
        elif currentCount > 0 and currentHours < 168 and currentHours > 0:
            startDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 0:00:00'
            endDate = str(today + datetime.timedelta(days=168 // 24)).replace('-', '/') + ' {}:00:00'.format(168 % 24)
        # 没有次数或时间
        else:
            msg = '{} 剩余次数{} 剩余时间{}这个月没有次数创建新的活动'.format(self.account, currentCount, currentHours)
            self.send_test_log(logName='全店铺打折', logType='Error',
                               msg=msg,
                               position='无法创建新的活动')
            return msg
        # 请求数据
        data = {
            '_csrf_token_': self.csrf_token,
            'identityCode': identityCode,
            'action': 'store_discount_action',
            'event_submit_do_create_promotion': 'anything',
            'promotionStartTime': startDate,
            'promotionEndTime': endDate,
            'storeNumber': store_number,
            'pcGroupDiscountJson': json.dumps([{"groupId": str(gruopId), "discount": '10'}, {"groupId": '0', "discount": ""}]),
            'mobileGroupDiscountJson': json.dumps(
                [{"groupId": str(gruopId), "discount": ""}, {"groupId": '0', "discount": ""}]),
            'promotionName': title,
            'hasPromo': False,
            'start-date-time': '1',  ### ?????
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['referer'] = url
        response = requests.post(url, headers=headers, data=data)
        print(response.text)
        if '没有权限' not in response.text:
            msg = '{} {} 发布失败'.format(self.account, activity_type)
            # self.send_test_log(logName='全店铺打折', logType='Error',
            #                    msg=msg)
            return msg
        else:
            log_data = {
                'Account': self.account,
                'Promotion_type': '限时限量折扣',
                'Channel': activity_type,
                'Promotion_Name': title,
                'Begin_time': startDate,
                'End_time': endDate,
                'ProductID': ','.join(self.product_ids),
            }
            self.log(log_data)
            self.send_test_log(logName='全店铺打折', logType='Run', msg='{} {}创建成功'.format(self.account, activity_type))

    # 修改活动
    def change(self):
        url = 'https://mypromotion.aliexpress.com/store/storediscount/edit.htm?spm=5261.10636610.300.11.1e783e5fJH02pR&promotion_id={}'.format(331302184)
        # date, gruopId = self.add_group()
        store_number = self.get_storeNumber('15002681752')
        identityCode = self.get_identityCode()
        data = {
            'storeNumber': store_number,
            'pcGroupDiscountJson': '[{groupId:"0",discount:"5"}]',
            'promotionEndTime': '2019/06/03 00:03:00',
            'action': 'store_discount_action',
            'identityCode': identityCode,
            'promotionStartTime': '2019/06/03 00:02:00',
            'promotionName': 'test0601',
            'mobileGroupDiscountJson': '[{groupId:"0",discount:""}]',
            'event_submit_do_edit_promotion': 'anything',
            '_csrf_token_': self.csrf_token,
            'hasPromo': False,
            'start-date-time': '3',
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, data=data, headers=headers)
        print(response)
        print(response.text)

    # 类的主函数
    def main(self, activity_type):
        # self.change()
        # 获取剩余时间，剩余次数以及活动类型
        currentHours, currentCount, activities_dict = self.get_hours_count()
        try:
            msg = self.create_new_activity(activities_dict[activity_type], activity_type)
            if msg is not None:
                return msg
        except KeyError as e:
            print(e)
            self.send_test_log(logName='全店铺打折', logType='Error', msg='{} {} 没有此活动'.format(self.account, activity_type),
                               position='获取现存活动失败')
            return '{} 没有此活动'.format(activity_type)


# 获取速卖通全部账号
def get_account():
    url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def main(entrance='MAIN', activity_type=None, account=None):
    # entrance = 'FLASK'
    # account_list = get_account()
    account_list = [
        'fb2@jakcom.com',
        # 'dongtian5@jakcom.com'
    ]
    if entrance == 'FLASK':
        if account not in account_list:
            return '请检查账号拼写是否正确'
        storeEvent = ShopDiscount(account)
        try:
            msg = storeEvent.main(activity_type)
            if msg is not None:
                return msg
        except Exception as e:
            print(e)
            storeEvent.send_test_log(logName='全店铺打折', logType='Error', msg='{} {} 全店铺打折出错'.format(account, activity_type))
    else:
        for account in account_list:
            storeEvent = ShopDiscount(account)
            # account = 'fb2@jakcom.com'
            try:
                activity_type = '创建活动'
                msg = storeEvent.main(activity_type)

                print(msg)
                continue
            except Exception as e:
                print(e)
                storeEvent.send_test_log(logName='全店铺打折', logType='Error', msg='{} {} 全店铺打折出错'.format(account, activity_type))


if __name__ == '__main__':
    main()
