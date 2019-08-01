# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: public.py
@time: 2019/5/25 15:36
@desc:  为alibaba 工作程序提供共用的方法模块
        （包括cookie的获取，请求头的构造，今日需要发布信息的获取，csrf_token的获取，cookie的检测）
"""
import re
import sys
import time
import json
import requests
# import urllib3
# urllib3.disable_warnings()

class Public(object):

    # 类的初始化
    def __init__(self, account, new=False):
        self.new = new
        self.account = account
        self.headers = self.get_headers()
        self.cookie = self.get_cookie()
        if self.cookie is None:
            time.sleep(300)
            self.__init__(account)
        # self.headers = self.get_headers()
        # self.check_cookie()

    # 获取cookie
    def get_cookie(self):
        url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
        response = requests.get(url)
        # 获取cookie 的正则表达式
        cookies = eval(response.text)
        # 初始化cookie
        for cookie in cookies:
            # 构造cookie
            if cookie[1] != self.account or cookie[2] is None or 'XSRF-TOKEN' not in cookie[2]:
                continue
            cook = cookie[2]
            # cook = 'ali_apache_id=183.185.139.137.1564272582478.407912.1; cna=BwfDFZ114xECAbe5i4kV/VDQ; aeu_cid=aa70c2a74e7049d4b609670632943667-1564308498445-00063-b6Jk1kus; _ga=GA1.2.1363255449.1564308505; _gid=GA1.2.1963644418.1564308505; aep_common_f=Mr1s7IklB+IHkodTceYwo0dmhRqTIqyODusGGej3OgQ8i60mXMVJzw==; UM_distinctid=16c380dddc3c-0e2e5852ba9dba-c343162-1fa400-16c380dddc4429; _lang=zh_CN; acs_usuc_t=x_csrf=10zu1tksjh4ca&acs_rt=f015d6c6984d4310a8f65b8d1e262455; _m_h5_tk=983e3b386ac54ba4dba5db4f56c8eddd_1564369587864; _m_h5_tk_enc=4b59e1ad22b3fc4fdacf7cebd637f400; xman_us_t=x_lid=cn1517949076kgdt&sign=y&x_user=3dhnxGFvLklyIqXJgENIZWMfEcEeffiRIICRawGVp6E=&ctoken=57wwksm8ywjq&need_popup=y&l_source=aliexpress; aep_usuc_t=ber_l=A0; xman_f=G2elNKWrQ9C5fw9TY+CeZNffFJ/+TzdifPuiRpMDkgdKdfO7xNKbuX0eDgO+4AGQKGk21ilVO5q/+xPpkiodO2bLt8e0cE0GJHQLwkkcmHaZElHoWdutwu/vxoEck9gG04GFqgs8Wr57ohwWsF/t6qs3yhp/5mXNuw0HZMH7lRyR2JCGFWOpTytrUG5CajSSEyWHQbEk8yf9HP0X21HzM5v/lrHYCxTcnZocC8vlBz9D4SUquBcvLNkPjtzfnPP11OA1wYR7gd+jWquVXN3FevVe1x+xs+zUp+O+WEfmEIgUyM2GEDxiKIu9fQ+SoyaRqYFEOS0iPa4YkHzV36BloUc5DvyrpkTgckHEbe6y4sU3d1undN0jh569RCyyNNoz0d0TWo9ffOY5BKPH7B9DedJhHXPGACk38in4/dnOUdF4IVIQc4k7YQ==; aep_usuc_f=isfm=y&site=glo&c_tp=USD&x_alimid=228082649&iss=y&s_locale=zh_CN&region=US&b_locale=en_US; xman_us_f=zero_order=y&x_locale=zh_CN&x_l=1&last_popup_time=1564272582502&x_user=CN|stone|tian|cnfm|228082649&no_popup_today=n&x_as_i=%7B%22aeuCID%22%3A%22aa70c2a74e7049d4b609670632943667-1564308498445-00063-b6Jk1kus%22%2C%22af%22%3A%221890605309%22%2C%22affiliateKey%22%3A%22b6Jk1kus%22%2C%22channel%22%3A%22AFFILIATE%22%2C%22cn%22%3A%2210008100042%22%2C%22cv%22%3A%221%22%2C%22ms%22%3A%221%22%2C%22src%22%3A%22promotion%22%2C%22tagtime%22%3A1564308498445%7D; intl_locale=zh_CN; ali_apache_track=ms=|mt=2|mid=cn1517949076kgdt; ali_apache_tracktmp=W_signed=Y; CNZZDATA1254571644=648585066-1564307245-%7C1564357462; intl_common_forever=FCphmxLsXG3yB8iQ+i2LTgBG2oIV3Xp5rotNI1ZKahJF9ajo+UQRgw==; xman_t=n/MQCbI6nJulh5BxXNDuDn7ztLwLT4pqZlTNjCI5Q/xyD041wCNpo5zhAocw0/sxHEYOZAUwGUzxYvmLslqpar8e0BxX2BX+/xiPaiFHUBkiX1iO7yBM+W60wRQordD4Q+e//UTJGJ3jrw0VEwU+RP1+hrn8GboPbGFa6EbtpyPyI0RU2jD6AyYPelxLqGvHwwMr9v5+oEMrkEh/msAcpzMNJPlC7Hn6f4MHOxva1NDmZ19d3p9lFwChfx91rpyK5yxmuiWtl4I6+OYCVMI7dLDKlT4TmlqrvWwnICfyK/pL7BhXPT8nOU8sgIt/n2p+83HUcaJfLCZ+Nzn/0ZrdZNSGAJpvNkQd+Q3gSKO62L1Kf2Wmzd3iSm/U920QIp1Yfandhqok/D0knIsvyhc8sYDOB/fo8P2raZ2ILnz4SCDCPZAkyOcW3vBXTVEcW1rwT3xdI+5/OjcT09GzhShmoVAWcL9aBMbxrzHrrGk1+lX7TkbPPcsqnTQXcNHB9GjCaguDqDVX/fZOlQDdcJFy9MqQ4pEU8u/VKr1FT5G7ts9l7pBijtCXS+LaB19609ynnF3uoXLhgItzMDcE+FzsnftiIfFJ+VL2ax+DJkdXizMuNi5UGlAA6rWmDAV0rf3sUZRtSjwg3TzuksS4/9dqEVQPhoO9FffO5prMXbL8nIVnPOSzIADO3g==; JSESSIONID=F6838D2D5C6276B110F1DE54588F6A30; l=cBPNZ34cqIyu5J-FBOfw5uI8LS7O6IRb8sPzw4OgiICP9d195mq5WZ3UJ68pCnGVLsivR3rCLlQLBy8SJPUshIPySiJLzRIF.; isg=BGZmyDytB8_u_9Noyyi4CG8bt9wo76uBbHiZ_lAPrglk0wftuNP7E5blL8_f-6IZ'
            self.headers['cookie'] = cook
            # self.headers['cookie'] =
            '1ankszfq0qe3t'
            cookieStatus = self.check_cookie()
            print(cookieStatus)
            if cookieStatus is True:
                return cook
            else:
                continue

        #     for i in cookie[2].split(';'):
        #         cookiesDict[i.split('=')[0]] = i.split('=')[1]
        # for k, v in cookiesDict.items():
        #     custom_cookie = custom_cookie + k + '=' + v + '; '
        #     # custom_cookie = custom_cookie + cookie['name'] + '={}; '.format(cookie['value'])
        # return custom_cookie

    # 构造请求头
    def get_headers(self):
        headers = {
            #  'authority': 'mypromotion.aliexpress.com',
            # # 'origin': 'https://mypromotion.aliexpress.com',
            # 'referer': 'https://mypromotion.aliexpress.com/store/limiteddiscount/create.htm?spm=5261.10636610.200.12.4b8a3e5fDy3Y8L',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            # 'scheme': 'https',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'upgrade-insecure-requests': '1',
            # 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            # # 'cookie': self.cookie,
            # 'cache-control': 'max-age=0',


            'authority': 'mypromotion.aliexpress.com',
            'method': 'GET',
            'path': '/store/fixeddiscount/list.htm?spm=5261.10636610.200.5.3c1c3e5fPhO1Zc',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'cache-control': 'max-age=0',
            # 'origin': 'https://trade.aliexpress.com',
            # 'referer': 'https://login.aliexpress.com/?flag=1&return_url=http%3A%2F%2Fmypromotion.aliexpress.com%2Fstore%2Ffixeddiscount%2Flist.htm%3Fspm%3D5261.10636610.200.5.3c1c3e5fPhO1Zc',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',

            # 'authority': 'afseller.aliexpress.com',
            # 'method': 'GET',
            # 'path': '/affiliate/productCommission/listProductCommission.do?isHot=true&pageSize=10&validIndex=1&invalidIndex=1',
            # 'scheme': 'https',
            # 'accept': 'application/json, text/plain, */*',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            # 'referer': 'https://afseller.aliexpress.com/affiliate/marketingPlanList.htm',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        }

        return headers

    # 获取 _tb_token_
    def get_tb_token(self):
        tb_token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        tb_token = re.findall(tb_token_re_compile, self.cookie)[0]
        return tb_token

    def get_csrf_token(self):
        url = 'http://photobank.aliexpress.com/photobank/uploader-new.htm'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r"csrfToken:'(.*?)'", re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.text)[0]
        return csrf_token

    def get_ctoken(self):
        try:
            ctoken_re_compile = re.compile(r'ctoken=(.*?)&', re.S)
            ctoken = re.findall(ctoken_re_compile, self.cookie)[0]
        except:
            ctoken_re_compile = re.compile(r'ctoken=(.*?);', re.S)
            ctoken = re.findall(ctoken_re_compile, self.cookie)[0]
        return ctoken

    # 发送测试日志
    def send_test_log(self, logName,logType, msg, position='0'):
        msg = str(msg)
        test_url = 'http://192.168.1.160:90/Log/Write'
        data = {
            'LogName': logName,
            'LogType': logType,
            'Position': position,
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': msg,
        }
        test_response = requests.post(test_url, data=data)
        print('test_response', test_response.text)

    def check_cookie(self):
        print('check cookie')
        if self.new is False:
            url = 'https://sellercenter.aliexpress.com/seller/index.htm'
            url = 'https://gsp.aliexpress.com/'
            response = requests.get(url, headers=self.headers)
            title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
            title = re.findall(title_re_compile, response.text)
            if len(title) == 0:
                return False
            print(title[0])
            if 'Manufacturer' in title[0]:
                return True
            else:
                return False
        else:
            url = 'https://mypromotion.aliexpress.com/wssellercrm/mail/create_marketing_mail_template.htm'
            response = requests.get(url, headers=self.headers)
            title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
            title = re.findall(title_re_compile, response.text)
            if len(title) == 0:
                return False
            print(title[0])
            if 'Manufacturer' in title[0]:
                return True
            else:
                return False

    def log(self, data):
        post_data = {
            'Account': data['Account'],
            'Promotion_type': data['Promotion_type'],
            'Channel': data['Channel'],
            'Promotion_Name': data['Promotion_Name'],
            'Begin_time': data['Begin_time'],
            'End_time': data['End_time'],
            'ProductID': data['ProductID']
        }
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/promotion_save'
        response = requests.post(url, data=post_data)
        print(response)
        print(response.text)

    def coupon_log(self, data):
        post_data = {
            'Account': data['Account'],
            'coupontype': data['coupontype'],
            'Starttime': data['Starttime'],
            'activityname': data['activityname'],
            'nominal_value': data['nominal_value'],
            'Condition': data['Condition'],
            'Endtime': data['Endtime'],
        }
        url = 'http://cs1.jakcom.it/Aliexpress_Promotion/coupon_logger'
        response = requests.post(url, data=post_data)
        print(response)
        print(response.text)
# Public('leliu3@jakcom.com')
