# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: main.py
@time: 2019/6/25 14:56
@desc:
"""
import sys, os
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'productInfoSpider'])