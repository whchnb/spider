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
import json
import requests


class Public(object):

    # 类的初始化
    def __init__(self, account):
        self.account = account
        self.cookie = self.get_cookie()
        self.headers = self.get_headers()
        self.tb_token = self.get_tb_token()
        self.ctoken = self.get_ctoken()
        # self.csrfToken = self.get_csrf_token()
        self.check_cookie()

    # 获取cookie
    def get_cookie(self):
        url = 'http://192.168.1.160:90/alibaba/get_cookie_byaccount?platform=Alibaba'
        response = requests.get(url)
        # 获取cookie 的正则表达式
        cookies = json.loads(response.text)
        # 初始化cookie
        custom_cookie = ''
        cookiesDict = {}
        for cookie in cookies:
            # 构造cookie
            if cookie['account'] != self.account or cookie['cookies'] is None:
                continue
            for i in cookie['cookies'].split(';'):
                cookiesDict[i.split('=')[0]] = '='.join(i.split('=')[1:])
        for k, v in cookiesDict.items():
            custom_cookie = custom_cookie + k + '=' + v + '; '
            # custom_cookie = custom_cookie + cookie['name'] + '={}; '.format(cookie['value'])
        return custom_cookie
        # return 'ali_apache_id=183.191.178.30.1557109691539.397124.9; cna=n4lWFZbRW2YCAbe/sh4Lxj33; UM_distinctid=16af89d82063ba-073d310012acd8-e353165-1fa400-16af89d8207d6; aep_common_f=eMDGONsKTvm7XmuxAkdzWk/SQrtl6Xj5SZVSbURyK712d7Ugy4bSbQ==; _m_h5_tk=d49a1ccf09158a073a60d2cff71c48f4_1559032696181; _m_h5_tk_enc=2fc6ffca9044d62cd675f4edd3a64011; ali_apache_tracktmp=W_signed=Y; intl_locale=zh_CN; acs_usuc_t=x_csrf=xpmk000mz6k_&acs_rt=9fbaa0b9bd7c46819b5cbc689012f346; xman_us_t=x_lid=jakcomtech&sign=y&x_user=4gw157E5lSYzGPZaER/s7D0uf/bC7XGX1qOHIGNM7eQ=&ctoken=lzklsocrw_d2&need_popup=y&l_source=aliexpress; aep_usuc_t=ber_l=A0; xman_f=A2T+eCTHbtmI8Sowls555A0M+Y63hG9l9MrkzYyjIEk6c4zExwM7dstnq3pgG9+ZV42WONmsSXHIbfLJEA4w9WmL69t/gANMUPIFt3DL6hFyYrDFzKih0BHuH/5bLtXk91ZgnoL3TXxwPjSBoMel6Q3q833gU93UVDmp/pxUqL8ekgS26AI5iv1/pDmbat5FNHynHGNE8LrvqXrjV6zfrlj3PmawfZPlJEq7PvDWpPXbJw0L0CKccSZvLRk47vW89TUtPUXLS4Q4NNq2Pe2PHvsufjTMTjF2W5NyITSVzH4IH+pVN5+QtTaGQFeYJ3x8eZTe791EbWMkDhoX20js+doYr3xRbg35dThRBeAzgwIbda8kHik7mc6XiX+yX9Vy4MlnDhmJpFs0UdiX9jIjeQ==; xman_us_f=zero_order=y&x_locale=zh_CN&x_l=1&last_popup_time=1557109691567&x_user=CN|Ady|Cao|cnfm|229737297&no_popup_today=n; aep_usuc_f=isfm=y&c_tp=USD&ispm=y&x_alimid=229737297&iss=y&s_locale=zh_CN&region=US&b_locale=en_US; ali_apache_track=ms=|mt=2|mid=jakcomtech; CNZZDATA1254571644=870484180-1558948231-%7C1559031627; JSESSIONID=9ABC324E88EF77D816F5A6A338AD0480; l=bBNV8y27v7TLxiDEBOfwquI8LS7tzCOXhsPzw4OgiICP_l6wupdlWZtKUixeC3GVa6d2J35fHFhYB-8s0y4Eh; isg=BC8v5TO2r0r3dqt25kjLn7hyvkP5fIJ24TlQBUG5kR64kEGSSKY-R2kCEoCu6Ftu; xman_t=JJbwjdcaNn7Ft8sqYMIyb504Z3zA/jBLh1f90PoLnAVeUWKg9hs6uBCuuMf4H2W1Bm8QwZRolShY6N6JGpC2MnlkXPjQof37HKUudWxE15P7xBbAXaVHAMIKwdGHHQqHs1Aqosra4eqGF+wZT9/lxCbRUJtFOoZm2k9FvA5tKKKy2Vkb8fJckejYxaNCYzZ8+zDJVDcWJRT9pUtASjiSGCBvUte8E5pyhqHzq3cF3skm4f2nl7qKO9DOsdK5xERT+x65LF6lrhj3PePXeM224Q/pshUTjMGz5G6/zhGG7s1Ap0EUCHfDH5MvJi4z5NOJ9p6iqzF83SS6Am4Z58ySwimSu5b2ruP5U48EHy+Q5PPu0pg1BGcsPT6xQlZcojYp5JKyu91rOtswwaSYQ1iqJA/5cVIRuSJeZOWv3yYhghT3iKxSkB/O/FWokzHEhw+nTafzQUaZ8hXxeCjznQlpSilCjgnvjYqB2/aalbIj1BuOKuru3nlDqbQH/FJP8cunaBw3OLO6cYopEDokxBDxLS52zE616zQqRuSB0+6k6TJfJP3/n5/mIOizfhd1mmMTAEw07WLGW1pemiIvSq8gbWcMegY5HR1esbdxFPpF/hK9uDnieNLxLp6Zq6j7XOR18Sy5hW5guouByPrkSPZ5Ew==; intl_common_forever=T6Slh5Mv89i+/HNtw109jTtJqUwbSDrheIbJ2IjCFi3F/MuEKNTA1A=='

    # 构造请求头
    def get_headers(self):
        headers = {
            'authority': 'data.alibaba.com',
            'method': 'GET',
            'path': '/product/overview',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            # 'accept': 'text/event-stream',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'cookie': self.cookie,
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }
        return headers

    # 获取 _tb_token_
    def get_tb_token(self):
        tb_token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        tb_token = re.findall(tb_token_re_compile, self.cookie)[0]
        return tb_token

    def get_csrf_token(self):
        url = 'https://hz-productposting.alibaba.com/product/products_manage.htm'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r" MANAGEAPP._csrf_ = {_csrf_token_ : '(.*?)'};", re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.text)[0]
        return csrf_token

    def get_ctoken(self):
        ctoken_re_compile = re.compile(r'ctoken=(.*?)&', re.S)
        ctoken = re.findall(ctoken_re_compile, self.cookie)[0]
        return ctoken

    # 发送测试日志
    def send_test_log(self, logName, logType, msg, position='0'):
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

    # cookie 的检测
    def check_cookie(self):
        url = 'https://alicrm.alibaba.com/'
        response = requests.get(url, headers=self.headers)
        title_re_compile = re.compile(r'<title>(.*?)</title>', re.S)
        title = re.findall(title_re_compile, response.text)[0]
        if title == '客户通':
            pass
        else:
            self.send_test_log(logName='alibaba账号', logType='Error', msg='{} cookie失效'.format(self.account),
                               position='alibaba账号 {} cookie失效'.format(self.account))
            sys.exit()
