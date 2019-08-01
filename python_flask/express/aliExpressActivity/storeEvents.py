# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: storeEvents.py
@time: 2019/5/31 17:30
@desc:  限时限量折扣
        1. 自建活动     每日2次（粉丝一次，新买家一次）
        2. 官方活动     手动触发
@step:
        1. 首先创建活动起止时间
        2. 获取活动对应的id，构造活动起始链接
        3. referer：起始链接，添加产品，发布活动
"""
import re
import json
import datetime
import requests
from w3lib.html import unquote_markup
from aliExpressActivity.public import Public
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class StoreEvent(Public):
    def __init__(self, account):
        self.account = account
        super(StoreEvent, self).__init__(self.account)
        self.csrf_token = self.get_csrf_token()

    # 获取每个活动的 promid
    def get_prominid(self, title):
        url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/list.htm'
        response = requests.get(url, headers=self.headers, verify=False)
        re_str = r'<td>\s*%s\s*<input type="hidden" name="promotionId" value="(.*?)">' % title
        promid_re_compile = re.compile(re_str, re.S)
        promid = re.findall(promid_re_compile, response.text)[0]
        return promid

    # 获取现有的活动类型
    def get_activities(self):
        url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/list.htm'
        response = requests.get(url, headers=self.headers, verify=False)
        activity_type_re_compile = re.compile(r'<a class="list-operate-create.*?"\s*href="(.*?)"\s*?.*?>(.*?)</a>',
                                              re.S)
        activities = re.findall(activity_type_re_compile, response.text)
        activities_dict = {i[1]: 'https://mypromotion.aliexpress.com' + i[0] for i in activities}
        return activities_dict

    # 获取identityCode 剩余时间，剩余次数以及默认标题
    def get_identityCode(self, url):
        # url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm'
        get_headers = self.headers
        get_response = requests.get(url, headers=get_headers, verify=False)
        # 获取identityCode
        identityCode_re_compile = re.compile(r'<input type="hidden" name="identityCode" value="(.*?)" />', re.S)
        identityCode = re.findall(identityCode_re_compile, get_response.text)[0]
        # 获取剩余次数及剩余时间
        currentCount_re_compile = re.compile(r"currentCount: '(.*?)'", re.S)
        currentHours_re_compile = re.compile(r"currentHours: '(.*?)'", re.S)
        currentCount = re.findall(currentCount_re_compile, get_response.text)[0]
        currentHours = re.findall(currentHours_re_compile, get_response.text)[0]
        # 获取默认标题
        default_title_re_compile = re.compile(r'<input type="text" name=""  value="(.*?)"  class="promotion-title"',
                                              re.S)
        title = re.findall(default_title_re_compile, get_response.text)[0]
        # return identityCode, 0, 10
        return identityCode, currentCount, currentHours, title

    # 创建活动时间
    def get_creata_activity_time(self, url, activity_type, objectOriented=None):
        print('创建活动时间')
        # url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm'
        # 获取identityCode 剩余次数，剩余时间，标题
        identityCode, currentCount, currentHours, title = self.get_identityCode(url)
        # 今天的日期
        today = datetime.datetime.now().date()
        # 构造活动标题
        if objectOriented == '新买家':
            title = 'New Buyer Special Offer {}'.format(str(today).replace('-', ''))
        elif objectOriented == '粉丝':
            title = 'Follow us Special Offer {}'.format(str(today).replace('-', ''))
        currentCount = int(currentCount)
        currentHours = int(currentHours)
        # 如果剩余次数大于0 并且剩余时间大于24小时， 正常设置
        if currentCount > 0 and currentHours >= 24:
            # 构造开始时间
            startDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 0:0:00'
            # 构造结束时间
            endDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 23:59:00'
        # 如果剩余次数大于0 并且剩余时间小于24， 将时间全部设置
        elif currentCount > 0 and currentHours < 24 and currentHours > 0:
            startDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' 0:0:00'
            endDate = str(today + datetime.timedelta(days=1)).replace('-', '/') + ' {}:00:00'.format(currentHours)
        # 如果剩余次数为0， 则表示这个月没有次数创建新的活动
        else:
            self.send_test_log(logName='限时限量折扣', logType='Error', msg='{} 次数{} 剩余时间{}'.format(self.account, currentCount, currentHours), position='没有更多的次数或更多的时间来创建活动')
            return '{} 次数{} 剩余时间{},这个月没有次数创建新的活动'.format(self.account, currentCount, currentHours)
        # 获取全部商品
        product_url = 'http://cs1.jakcom.it/aliexpress_promotion/promotion_productlist?account={}'.format(
            self.account)
        # 获取全部商品id
        product_ids = self.get_product(product_url)
        if isinstance(product_ids, str):
            return '{} 没有获取到新的商品'.format(self.account)
        # 创建时间请求数据
        data = {
            '_csrf_token_': self.csrf_token,
            'identityCode': identityCode,
            'action': 'limited_discount_action',
            'event_submit_do_create_promotion': 'anything',
            '_fms.c._0.p': title,
            '_fms.c._0.pr': startDate,
            '_fms.c._0.pro': endDate,
            '_fms.c._0.s': '',
            'setRealTimeReleasePromo': False,
            'hasPromo': False,
        }
        post_headers = self.headers
        post_headers['method'] = 'POST'
        post_headers['content-type'] = 'application/x-www-form-urlencoded'
        post_headers['referer'] = url
        response = requests.post(url, headers=post_headers, data=data)
        if '没有权限' in response.text:
            # 获取刚刚创建好的活动promid
            promid = self.get_prominid(title)
            # 发布新活动
            msg = self.send_new_activity(promid, objectOriented=objectOriented, url=url, activity_type=activity_type, timeData=data)
            if msg is not None:
                return msg
        else:
            self.send_test_log(logName='限时限量折扣', logType='Error', msg='{} {} {}-{}'.format(self.account, activity_type, startDate, endDate), position='创建活动时间')

    # 获取商品属性
    def get_sku_attr(self, promid, productids):
        print(productids)
        print('正在获取sku 属性')
        url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/promProductManage.htm?promId={}'.format(promid)
        data = {
            '_csrf_token_': self.csrf_token,
            'promId': promid,
            'productIds': productids,
            'promDescription': '',
            'productObjects': [],
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, data=data, headers=headers)
        sku_attr_re_compile = re.compile(r'<input type="hidden" value="(.*?)" ', re.S)
        sku_attr = unquote_markup(re.findall(sku_attr_re_compile, response.text)[0])
        return eval(sku_attr)

    # 发布新活动
    def send_new_activity(self, promid, url, activity_type, timeData, objectOriented=None):
        print('发布新活动')
        # 重新获取identityCode
        identityCode = self.get_identityCode(url)[0]
        # 共用的数据
        data = {
            '_csrf_token_': self.csrf_token,
            'identityCode': identityCode,
            'action': 'limited_discount_action',
            'event_submit_do_add_store_prom_product': 'anything',
            'promId': '',
            'existStoreFansDiscount': -1
        }
        # objectOriented 为 新客户、 粉丝
        # objectOriented 不为空说明是创建活动
        if objectOriented is not None:
            # 获取全部商品
            product_url = 'http://cs1.jakcom.it/aliexpress_promotion/promotion_productlist?account={}'.format(self.account)
            # 获取全部商品id
            product_ids = self.get_product(product_url)
            # product_ids = ['33004310831', '32869445765', '32957243474', '32870168008', '32972845774', '32869505927', '32957957547', '32950567621', '32918922408', '32909616587', '32918981944', '33005763280', '32910224723', '32958480821']
            print(product_ids)
            if type(product_ids) is str:
                return product_ids
            products = []
            for product_id in product_ids:
                try:
                    sku_attr = self.get_sku_attr(promid, product_id)
                    # sys.exit()
                    detail = {
                        "productId": product_id,
                        "skuInventoryInfo": sku_attr,
                        "limitProductNumMax": 10,  # 没人限购
                        "discountInfo": [
                            {"terminal": "all",  # 折扣类型
                             "discount": 10},
                            {"terminal": "mobile",  # 手机折扣
                             "discount": 12}]
                    }
                    products.append(detail)
                except:
                    continue
            data['storeClubDiscountRate'] = 5  # 额外折扣
            data['storeFansShowFlag'] = True
            data['productObjects'] = json.dumps(products)
            if objectOriented == '新买家':
                """
                extraDiscountType: storeNewUserDiscount
                """
                url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/promProductManage.htm?promId={}'.format(
                    promid)
                data['extraDiscountType'] = 'storeNewUserDiscount'
            else:
                """
                extraDiscountType: storeFans
                """
                url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/promProductManage.htm?promId={}'.format(
                    promid)
                # data['productIds'] = ''
                data['extraDiscountType'] = 'storeFans'
                print(len(products))
                # data['actionType'] = 'EDIT'
        # objectOriented 为空则为flask 的官方活动
        else:
            product_url = 'http://cs1.jakcom.it/aliexpress_promotion/promotion_productlistbycar?account={}&operateType=edit'.format(self.account)
            product_ids = self.get_product(product_url)
            if type(product_ids) is str:
                return product_ids
            products = []
            for product_id in product_ids:
                detail = {
                    "productId": product_id,
                    "skuInventoryInfo": [
                        {"quantity": 0}
                    ],
                    "limitProductNumMax": 10,
                    "discountInfo": [
                        {"terminal": "all", "discount": 20}
                    ]
                }
                products.append(detail)
            data['storeClubDiscountRate'] = 0  # 额外折扣
            data['storeFansShowFlag'] = True
            data['extraDiscountType'] = ''
            data['productObjects'] = json.dumps(products)
            url = 'https://mypromotion.aliexpress.com/store/limiteddiscount/promProductManage.htm?promId={}'.format(
                promid)
        post_headers = self.headers
        post_headers['method'] = 'POST'
        post_headers['content-type'] = 'application/x-www-form-urlencoded'
        post_headers[
            'referer'] = 'https://mypromotion.aliexpress.com/store/limiteddiscount/promProductManage.htm?promId={}'.format(
            promid)
        response = requests.post(url, data=data, headers=post_headers, verify=False)
        # print(data)
        print(response.text)
        if '没有权限' in response.text:
            log_data = {
                'Account': self.account,
                'Promotion_type': '限时限量折扣',
                'Channel': activity_type,
                'Promotion_Name': timeData['_fms.c._0.p'],
                'Begin_time': timeData['_fms.c._0.pr'],
                'End_time': timeData['_fms.c._0.pro'],
                'ProductID': ','.join(product_ids),
            }
            print('{} {} 创建成功'.format(self.account, activity_type))
            self.log(log_data)
            self.send_test_log(logName='限时限量折扣', logType='Run', msg='{} {} 创建成功'.format(self.account, activity_type), position='创建活动')
        else:
            print('err')

            self.send_test_log(logName='限时限量折扣', logType='Error',msg='{} {} {}'.format(self.account, activity_type, data), position='创建活动')

    # 获取商品id
    def get_product(self, url):
        # url = 'http://cs1.jakcom.it/aliexpress_promotion/promotion_productlist?account={}'.format(self.account)
        response = requests.get(url)
        datas = json.loads(response.text)
        product_ids = []
        if len(datas) != 0:
            for data in datas:
                product_ids.append(data['Product_ID'])
            # product_ids.remove('32913470642')
            # product_ids.remove('32933106122')
            # product_ids.remove('32825929158')
            return product_ids
        else:
            msg = '{} 没有获取到商品'.format(self.account)
            self.send_test_log(logName='限时限量活动', logType='Error', msg=msg)
            return msg

    # 类的主函数
    def main(self, activity_type):
        # product_ids = self.get_product()
        # 从网页获取现有的活动类型及对应链接
        activities_dict = self.get_activities()
        # activity_type = '参加2019年6月大促'
        if activity_type == '创建活动':
            objectOrienteds = [
                '新买家',
                '粉丝'
            ]
            for objectOriented in objectOrienteds:
                msg = self.get_creata_activity_time(activities_dict[activity_type], activity_type, objectOriented)
                if msg is not None:
                    return msg
                # title = 'Follow us Special Offer 20190605' if objectOriented == '粉丝' else 'New Buyer Special Offer 20190605'
                # promid = self.get_prominid(title)
                # data = {
                #     '_fms.c._0.p': title,
                #     '_fms.c._0.pr': '2019/06/06 0:00:00',
                #     '_fms.c._0.pro': '2019/06/06 23:59:00',
                # }
                # msg = self.send_new_activity(promid, objectOriented=objectOriented, url=activities_dict[activity_type],
                #                              activity_type=activity_type, timeData=data)
                # if msg is not None:
                #     return msg
        else:
            try:
                msg = self.get_creata_activity_time(activities_dict[activity_type], activity_type)
                if msg is not None:
                    return msg
            except KeyError as e:
                print(e)
                self.send_test_log(logName='限时限量折扣', logType='Error', msg='{} {} 没有此活动'.format(self.account, activity_type), position='获取现存活动失败')
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
    # account_list = ['13333437345@163.com']
    # account_list = ['fb2@jakcom.com']
    account_list = [
        # 'fb2@jakcom.com',
        # '13333437345@163.com',
        # 'jikang4@jakcom.com',
        # 'jikang5@jakcom.com',
        # 'dongtian4@jakcom.com',
        # 'jikang6@jakcom.com',
        # 'dongtian5@jakcom.com',
        # 'for@imtimer.com',
        # 'jikong1@jakcom.com',
        # 'jikong2@jakcom.com',
        # 'dongtian2@jakcom.com',
        'jikong2@jakcom.com',
        'dongtian3@jakcom.com',
        'leliu1@jakcom.com',
        'leliu2@jakcom.com',
        'leliu3@jakcom.com'
    ]
    print(account_list)
    if entrance == 'FLASK':
        if account not in account_list:
            return '请检查账号{} 拼写是否正确'.format(account)
        storeEvent = StoreEvent(account)
        try:
            msg = storeEvent.main(activity_type)
            if msg is not None:
                return msg
        except Exception as e:
            print(e)
            storeEvent.send_test_log(logName='限时限量折扣', logType='Error', msg='{} {} 限时限量折扣出错'.format(account, activity_type))
    else:
        for account in account_list:
            print(account)
            storeEvent = StoreEvent(account)
            # account = 'fb2@jakcom.com'
            try:
                activity_type = '创建活动'
                msg = storeEvent.main(activity_type)
                print(msg)
            except Exception as e:
                print(e)
                storeEvent.send_test_log(logName='限时限量折扣', logType='Error', msg='{} {} 限时限量折扣出错'.format(account, activity_type))


if __name__ == '__main__':
    main()