# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: timing.py
@time: 2019/5/8 17:57
@desc: 每日01:00 定时执行营销任务
"""
import os
from apscheduler.schedulers.blocking import BlockingScheduler


def job():
    os.system(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\python.exe D:/Main/Promotion/alibabaMarket.py')


if __name__ == '__main__':
    # BlockingScheduler
    scheduler = BlockingScheduler()
    # scheduler.add_job(job, 'cron', hour=1, minute=00)
    scheduler.add_job(job, 'cron', hour=1, minute=1)
    scheduler.add_job(job, 'cron', hour=3, minute=1)
    scheduler.start()
