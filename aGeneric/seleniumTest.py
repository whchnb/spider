# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: seleniumTest.py
@time: 2019/7/16 14:05
@desc:
"""
import re
import time
import datetime
import requests
import threading
from selenium import webdriver
from urllib.parse import urljoin
from aliExpress.public import Public
from selenium.webdriver.chrome.options import Options


class SeleniumTest:
    # 类的初始化
    def __init__(self, cookie, url):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        self.cookie = cookie
        # 请求目标链接
        self.url = url
        # 构造浏览器对象
        self.browser = self.launch_web()
        self.browser.get('https://mypromotion.aliexpress.com/wssellercrm/mail/create_marketing_mail_template.htm')
        time.sleep(5)
        print(self.browser.get_cookies())
        self.quit()

    #  启动无头浏览器
    def launch_web(self):
        """
        启动无头浏览器
        :return: 浏览器对象
        """
        print('正在启动浏览器')
        # 浏览器设置
        chrome_options = Options()
        # 设置无头
        # chrome_options.add_argument('--headless')
        # 加上这个属性来规避bug
        chrome_options.add_argument('disable-gpu')
        # 设置浏览器分辨率
        # chrome_options.add_argument('window-size=1200,1100')
        # 不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 配置浏览器
        chrome_options.add_experimental_option("prefs", prefs)
        # 启动浏览器
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.maximize_window()
        # 使用浏览器打开链接
        browser.get(self.url)
        # 删除浏览器生成的cookie
        browser.delete_all_cookies()
        # 获取账户对应cookie
        cookie_list = self.cookie
        for cookie in cookie_list.split(';'):
            # 将cookie添加到浏览器中
            try:
                browser.add_cookie({'name': cookie.split('=')[0], 'domain': '.aliexpress.com', 'value': ''.join(cookie.split('=')[1:])})
            except:
                pass
        print('cookie 更改成功')
        # 重新打开链接
        browser.get(self.url)
        return browser

    def quit(self):
        self.browser.quit()

cookie = 'ali_apache_id=61.134.228.59.1561373648868.378749.6;t=6cb9283b7dd6d819513fbc98409c0b3f;cna=QSBYFaliTAwCAbe/sh7s0jEq;last_ltc_icbu_icbu=cHdk;UM_distinctid=16ba75eb1d51b8-0622207461176b-404b032d-13c680-16ba75eb1d6298;isg=BO3tuP05TGF-pCg49aBEf9Ii_Imn4iBYnbM56y_yKQTzpg1Y9Zox7Dt3lDrlJjnU;l=cBaJulbrvDHe0aeiBOCw5uI8LoQOSIRAguPRwCYHi_5pK6TsH07OkDNtZF96cjWd9a8H45fyK2e9-etkwbuBUt5o1O-c.;ali_apache_track=mt=3|mid=jakcomb2b;ali_apache_tracktmp=;xman_us_t=ctoken=t8lekwwkmcrb&x_user=CsyQge0gVTBOBKJn/nZzgP6C9o0VtziscD+QZJcrSrc=&x_lid=cn1517949076kgdt&sign=y&need_popup=y;xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1561373648877&x_user=CN|stone|tian|cnfm|228082649&no_popup_today=n;acs_usuc_t=acs_rt=3c1b539b421240e2a31d97aab4062f06;intl_locale=zh_CN;xman_t=O3iDjo2uxbWFWeZPD9E16CvfFlJ5QssbToNuCAXK+S7YuFJqqKgHO6VOFSXW9mOMvIwzM/G5FFkAAi9VIWsyiA0XSVxUOEZsf8auANper8tMfgXH9NXV2C3d6e2JQ22PMMEWg6bo/cUKTAMy66TtBn+k94E/07b7j0oAejoX3kN+zL491K2CIMyYYy2s6fGqKIiknr7twKdHmejTztPooE4d0/uOcHpxkGbdzE8VJrdK91kii4sIfp4uDpMa1jk1aKDREeUWdBEJwjNeV6yC5vJcu19LHIF64XlFevUMln2TNvMXTpoLb7E2z6R6YOaGQpa7iqoZWQc/ybGDr1Dty8RjXUmdOSfMqVqLSFvlglQAx0AdyXD1fp0laDWytj/EzydTdlLtARQgqR6bnt0qwlvumHVF9gMUhAiXCW1lFRTXewdCtKYwWEuWxWhVpxYq32dUqkw0T03BXd79t9ACj6Z230fcM//zFeBToB/fgjzHpUsSSd7s6MgL3tK/msTDpLwki4qDF4jcer0pXoKn0bslRkGsuxpfb86e4nlyKwWBjT1Pn18McgFpwAVuY8cPSqrsFU1SWYa/wCsNCxE/RZdl74V/E2DeJXfUop+2BkwHISKhJMFMWhRVetwDCwBJn6SSCuc3QVIqRMCGXuDmRHGVzRlHyCdB2/jd/XXW+aLPEjv2dbGAtyhaV23IXX74s3xBVs0B3TcBASOSZVvlxAvOwK97J125n85+Mw/F5WU=;intl_common_forever=HxMp1mKEm8rky9+nuTM8knaX7OreXT1FGAFaSeCjD9D64iBDsU+4kw==;xman_f=sNBAU91WLWfQgGR8z7xVtYamWMxHLVv0XLwut5LkRwLI3siRatSobJJMbTcWDfOuJskH26M+7iKCAgv19FeoCXpnANmFPqkJN3A6te36pbBMbmnpsxbbusjqbWTJUDVuJEpCNDfFqQYTbiXYn9vZ9HNxymL7FzS2cRVQxr0G2a9/2QXoarAINb+k96NYq1oaWm7bHAePH92WCXDVtX+h7s9sBM4l79BxYF7T8uY/hPV4JCUYo6iE49zB8FGL52ypPgqSrJiYIfgixqZ0/u77Tr87zjjpVfjaF2ytNmgEIJVhBfaef9+hwk2ipBLuGW85C5sSvympLIxJifSXYKZaJlyWMyl55F4+U8HreL9wivmzGPCKYYzugUc6fg/Qb/0qgvkhOzgVgv2C2IavY1eMr4pbTpzeok6T;_hvn_login=13;cookie2=1f478fa7755cb71eb2a0412aa11bb835;csg=94619cb6;_tb_token_=8e5b637ef138acs_usuc_t=x_csrf=9g7e7dy4muxp&acs_rt=3c1b539b421240e2a31d97aab4062f06;xman_t=Ly6+u6NmBPHm/HXaEICddC8xikHRRWNcXDBZnozrokg+Rqedie5RZ/pfF5Y3yVjtyNQWSUvfhcSP4FKJ465YCwBFk//i6nEl1nL6Bt0H9uzlHyFmLr8W9RPDIzMVelagVhUJAzk2ga9vdTaNfHgdyDSVgNLm3Zwbk1ZOs054FZqgqAsmzynwFSIVP6ImtiYh+XVsx6F4x14EO5Qk0GbOYLY/57yqNZ6+X2GLlRk+OMunYsQPPtfq0pNJaxyWuxrGqme9P2+0BbnrbzJ2DjuQVRBUpUAPwjKp0TQqkx265STJuQgb7qY3sM4Kvt1D8TYqxPbcXV6lbVuCpghKhi5JN7eIHq9ExanZdy74sh3JTGe+71+yY47hfVkROUcf/gjIiFEADYGY5qVc6cWtuL03vZj09d9Q00F0snJN2bwmBM1iij3X8wO+OYEc7rOyTtRxjtI4gcup54BQmOfWZIwAl8oPU5gEF2+nwLggpLZo8/PNQkcWiW4j3dywXsXFKMqeVjvAdaRIlgj4OZ4Ca37wqUPF7ZHhJYn++poloIqNSdztfPtOLoM4fVKFY3YlB+XUrmEQSSO0oGXDs9MERd9nXXAHydruiBSypuDsl3ZtOCxGOmE9CRMBo8tFuEK4sSc8NC8mhf2d0Uk00086EapMeFVSLWDVkTN7HF+32qrvN2IGlR8kN2mIgKu3CxaSRckaAZhU2zcuC+vE4BwGRR9YM9Achj9HFdFGM829EbcAMk8=;XSRF-TOKEN=e948d7b9-fb7d-4444-8df6-e72ef9219109'
url = 'https://gsp.aliexpress.com/'
a = SeleniumTest(cookie, url)
