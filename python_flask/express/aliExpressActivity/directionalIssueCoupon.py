# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: directionalIssueCoupon.py
@time: 2019/6/4 11:13
@desc:  定向发放型优惠券    接口调用
@step:  1. 首先需要添加优惠券
        2. 通过创建好的优惠券标题在列表页查找创建好的活动id
        3. 通过customerid 查找到aliStr
        4. 构造请求，选择客户定向发放优惠券
"""
import re
import datetime
import requests
from aliExpressActivity.public import Public


class DirectionalIssueCoupon(Public):
    def __init__(self, account, buyerID, value):
        self.account = account
        self.buyerID = buyerID
        self.value = value
        super(DirectionalIssueCoupon, self).__init__(self.account)
        self.csrf_token = self.get_csrf_token()

    # 获取identityCode和剩余次数
    def get_identityCode(self):
        url = 'https://mypromotion.aliexpress.com/store/coupon/create.htm'
        get_headers = self.headers
        get_response = requests.get(url, headers=get_headers)
        identityCode_re_compile = re.compile(r'<input type="hidden" name="identityCode" value="(.*?)" />', re.S)
        identityCode = re.findall(identityCode_re_compile, get_response.text)[0]
        currentCount_re_compile = re.compile(r'<strong>定向发放型优惠劵活动</strong>.*?<em>(.*?)</em> 个', re.S)
        currentCount = re.findall(currentCount_re_compile, get_response.text)[0]
        return identityCode, currentCount

    # 创建优惠券
    def submit(self):
        print('创建优惠券')
        # 回去identityCode 以及剩余创建次数
        identityCode, currentCount = self.get_identityCode()
        if int(currentCount) == 0:
            msg = '{} 定向发放型优惠劵活动 本月没有次数继续创建'.format(self.account)
            self.send_test_log(logName='定向发放型优惠券', logType='Run', msg='{} 创建失败 {}'.format(self.account, msg))
            return msg
        # 标题
        title = '{} Coupon {} '.format(self.buyerID, self.value)
        # 构造开始时间
        today = datetime.datetime.now().date()
        startDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 0:1:00'
        # 构造结束时间
        endDate = str(today + datetime.timedelta(days=7)).replace('-', '/') + ' 23:59:00'
        couponEndDate = str(today + datetime.timedelta(days=8)).replace('-', '/') + ' 00:00:00'
        data= {
            '_csrf_token_': self.csrf_token,
            'identityCode': identityCode,
            'action': 'direct_store_coupon_action',
            'event_submit_do_create': 'anything',
            'acquireEndDate': endDate,    # 活动结束时间        活动结束时间必须大于使用开始时间
            'couponConsumeStartDate': startDate,    # 使用开始时间
            'couponConsumeEndDate': couponEndDate,      # 使用结束时间        优惠券有效期结束时间必须大于活动结束时间
            'productsList': '',
            'activityType': '1',
            'activityName': title,     # 活动名称
            'rangeType': '',
            'denomination': self.value,        # 面额值
            'totalReleaseNum': '1',     # 发放总数量
            'hasUseCondtion': 'n',
            'couponConsumeDateType': '2',
        }
        url = 'https://mypromotion.aliexpress.com/store/directcoupon/create.htm?t=2'
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['referer'] = url
        response = requests.post(url, headers=headers, data=data)
        # 如果页面中存在没有权限， 表明优惠券创建成功 可以选择客户发放
        if '没有权限' in response.text:
            print('创建成功')
            msg = self.send_coupon(title, endDate)
            return msg
        else:
            msg = '{} 优惠券创建失败'.format(self.account)
            self.send_test_log(logName='定向发放型优惠券', logType='Error', msg=msg)
            return msg

    # 通过标题获取活动id
    def get_activity_id(self, title):
        url = 'https://mypromotion.aliexpress.com/store/directcoupon/list.htm'
        response = requests.get(url, headers=self.headers)
        print(response.text)
        re_str = r'<tr  activityId="(.*?)">[\s,\w,\W]*?%s' % title
        print(re_str)
        activityId_re_compile = re.compile(re_str.strip(), re.S)
        activityId = re.findall(activityId_re_compile, response.text)[0]
        return activityId

    # 发送优惠券 1871791945 Coupon 1
    def send_coupon(self, title, endDate):
        # 获取去活动id
        activityId = self.get_activity_id(title)
        params = {
            'customerid': self.buyerID
        }
        # 通过customerid 获取buyerAliIdStr
        buyerAliIdStr = requests.get('http://cs1.jakcom.it/Aliexpress_Customer/getbuyeridstr', params=params).text[1:-1]
        data = {
            '_csrf_token_': self.csrf_token,
            'action': 'direct_store_coupon_action',
            'buyerAliIdStr': buyerAliIdStr,
            'activityId': activityId,
            'event_submit_do_send_coupon': 'anything',
        }
        url = 'https://mypromotion.aliexpress.com/store/customer/crm_customer_list.htm?activityId={}&page=1'.format(activityId)
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['referer'] = url
        headers['method'] = 'POST'
        response = requests.post(url, headers=headers, data=data)
        # 获取发放优惠券响应状态码
        status_re_colpile = re.compile(r'success: (.*?),', re.S)
        status = re.findall(status_re_colpile, response.text)[0]
        print(status)
        # 如果状态码为 true  表明发放成功
        if status == 'true':
            data = {
                'Account': self.account,
                'coupontype': '定向发放型优惠券',
                'Starttime': str(datetime.datetime.now()),
                'activityname': title,
                'nominal_value': self.value,
                'Condition': '不限',
                'Endtime': endDate,
            }
            self.coupon_log(data)
            msg = '{} 定向发放型优惠券发放成功'.format(self.account)
            self.send_test_log(logName='定向发放型优惠券', logType='Run', msg=msg)
            return msg
        else:
            msg = '{} 定向发放型优惠券发放失败'.format(self.account)
            return msg

    def main(self):
        msg = self.submit()
        if msg is not None:
            return msg


# 获取速卖通全部账号
def get_account():
    url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def main(account, buyerID, value):
    account_list = get_account()
    if account not in account_list:
        msg = '{} 不存在，请检查账号拼写是否正确'
        return msg
    # account_list = ['fb2@jakcom.com']
    # buyerID = 793405141    # 客户id
    # account = ''    # 账号
    # value = 1      # 金额
    collectionCoupon = DirectionalIssueCoupon(account, buyerID, value)
    collectionCoupon.main()
    # collectionCoupon.send_coupon('793405141 Coupon 1 test', '2019/02/06')


if __name__ == '__main__':
    main('dongtian5@jakcom.com', 1871791945, 1)