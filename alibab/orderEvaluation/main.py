# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: run.py
@time: 2019/5/28 9:31
@desc:
"""
import sys, os
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(['scrapy', 'crawl', 'orderEvaluationInfoSpider'])