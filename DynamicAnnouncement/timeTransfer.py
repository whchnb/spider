# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: timeTransfer.py
@time: 2019/5/23 15:55
@desc:
"""
import time

def transfer(statDate):
    """
    时间戳转时间
    :param statDate:
    :return:
    """
    statDate = time.localtime(int(str(statDate)[:10]))
    return time.strftime("%Y-%m-%d", statDate)

def timeTransfer(date):
    """
    时间转时间戳
    :param date:
    :return:
    """
    timestamp = time.mktime(time.strptime(date, "%Y-%m-%d"))
    return str(timestamp).replace('.', '') + '00'


# print(transfer(1556772378000))