# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: flashSale.py
@time: 2019/6/19 13:37
@desc:
"""
import re
import json
import time
import random
import requests
import datetime
from DynamicAnnouncement.public import Public


class FlashSale(Public):
    def __init__(self):
        super(FlashSale, self).__init__()
        self.csrf_token = self.get_csrf_token()

    # 获取csrf_token
    def get_csrf_token(self):
        url = 'https://widget.1688.com/front/ajax/bridge.html'
        response = requests.get(url, headers=self.headers)
        csrf_token_re_compile = re.compile(r'__mbox_csrf_token=(.*?);', re.S)
        csrf_token = re.findall(csrf_token_re_compile, response.headers['Set-Cookie'])[0]
        self.cookie = self.cookie + '__mbox_csrf_token=%s' % csrf_token
        self.headers['cookie'] = self.cookie
        return csrf_token

