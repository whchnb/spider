# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: timing.py
@time: 2019/5/8 17:57
@desc: 每日00:10 定时执行营销任务
"""
import os
from apscheduler.schedulers.blocking import BlockingScheduler


def announce():
    os.system(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe D:/Main/DynamicAnnouncement/announce.py')

def microDynamic():
    os.system(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe D:/Main/DynamicAnnouncement/microDynamic.py')

def pickUpNews_with_selenium():
    os.system(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe D:/Main/DynamicAnnouncement/announce.py')

def distribution():
    os.system(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe D:/Main/DynamicAnnouncement/distribution.py')


if __name__ == '__main__':
    hour = 00
    minute = 10
    scheduler = BlockingScheduler()
    scheduler.add_job(announce, 'cron', hour=hour, minute=minute)                          # 淘货源公告
    scheduler.add_job(microDynamic, 'cron', hour=hour, minute=minute)                      # 微供动态
    scheduler.add_job(distribution, 'cron', hour=hour, minute=minute)                      # 分销客
    scheduler.add_job(pickUpNews_with_selenium, 'cron', hour=hour, minute=minute)          # 挑货动态
    scheduler.start()
