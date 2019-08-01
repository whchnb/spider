# 导入系统模块
import os
import time
import json
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor


sycmstatus = False
lkwxstatus = False
vipstatus = False


def test1():
    print(1, os.getpid())
    global sycmstatus
    sycmstatus = True
    time.sleep(20)
    print(21)
    sycmstatus_status = True
    return sycmstatus_status


def test2():
    print(2, os.getpid())
    global lkwxstatus
    lkwxstatus = True
    time.sleep(20)
    print(22)
    lkwxstatus_status = True
    return lkwxstatus_status


def test3():
    print(3)
    global vipstatus
    vipstatus = True
    time.sleep(20)
    print(23)
    vipstatus_status = True
    return vipstatus_status


def kill_job():
    for job in jobs:
        print(job.set_running_or_notify_cancel)
        if job.result() is True:
            threading.enumerate().remove(job)
        # print(job.result())




def func():
    os.system("cls")
    print('正在执行 Python 本地定时任务，当前时间：%s ' % time.strftime('%Y-%m-%d %H:%M:%S'))
    print('当前存在的线程有', threading.enumerate()[1:])
    print('当前共存在{}条线程'.format(int(threading.active_count() - 1)))
    pool.submit(kill_job)
    # 当前时间
    today = datetime.datetime.now().date()
    now = time.strftime('%H:%M')
    print(now)
    now = str(now)
    # 执行生意参谋 老客维系 会员列表 分销商管理 任务 每日18:00运行
    if now > '13:00':
        if sycmstatus is False:
            sycmstatus_status = pool.submit(test1)
            jobs.append(sycmstatus_status)
            print(sycmstatus_status.set_running_or_notify_cancel)
            print(dir(sycmstatus_status))
        if lkwxstatus is False:
            lkwxstatus_status = pool.submit(test2)
            jobs.append(lkwxstatus_status)
        if vipstatus is False:
            vipstatus_status = pool.submit(test3)
            jobs.append(vipstatus_status)

    test = threading.Timer(5, func)
    test.start()


if __name__ == '__main__':
    pool = ThreadPoolExecutor(1)
    jobs = []
    test = threading.Timer(0, func)
    test.start()
