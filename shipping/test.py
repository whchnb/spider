# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: test.py
@time: 2019/6/21 11:49
@desc:
"""
import requests


url = 'https://httpbin.org/ip'
proxies = {
    'http': 'https://192.168.1.67',
    'https:': 'https://192.168.1.67'
}
response = requests.get(url, proxies=proxies)
print(response.text)