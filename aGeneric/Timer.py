"""
本地任务定时器

"""

# 导入自制模块
from Cn1688.product_coupon import ProductCoupon
from Cn1688.target_coupon import TargetCoupon
from Cn1688 import announce, distribution, microDynamic
from Cn1688 import newPassengerTreasure_selenium
from Cn1688 import newProducts_selenium
from Cn1688 import pickUpNews_with_selenium
from Cn1688 import invite_selenium
from Cn1688 import flashSale_selenium
from Alibaba import alibabaFan_with_selenium
from Alibaba import alibabaMarket

# 导入系统模块
import os
import time
import datetime
import threading


def nine_zero():
    # 发放 越努力越幸运 定向优惠券
    go = TargetCoupon()
    go.send_lucky_coupon()
    time.sleep(60)

def zero_five():
    # 创建 新品限时优惠
    go = ProductCoupon()
    create_new_products_coupon = threading.Thread(target=go.create_new_products_coupon, args=())
    create_new_products_coupon.start()
    time.sleep(10)
    # 创建 今日特价优惠
    create_special_price_products_coupon = threading.Thread(target=go.create_special_price_products_coupon, args=())
    create_special_price_products_coupon.start()
    time.sleep(10)
    # 删除 已结束
    delete_expire_product_coupons = threading.Thread(target=go.delete_expire_product_coupons, args=())
    delete_expire_product_coupons.start()
    time.sleep(60)

def zero_ten():
    # 发布 淘货源公告
    announce = threading.Thread(target=announce.announce, args=())
    announce.start()
    time.sleep(10)
    # 推广商品 分销客
    distribution = threading.Thread(target=distribution.distribution, args=())
    distribution.start()
    time.sleep(10)
    # 发布 微供动态
    microDynamic = threading.Thread(target=microDynamic.microDynamic, args=())
    microDynamic.start()
    time.sleep(10)
    # 发布 挑货动态
    pickUpNews = threading.Thread(target=pickUpNews_with_selenium.pickUpNews, args=())
    pickUpNews.start()
    time.sleep(40)

def one_zero():
    # 执行 Alibaba 粉丝通任务
    alibaba_fans_moment = threading.Thread(target=alibabaFan_with_selenium.alibaba_fans_moment, args=())
    alibaba_fans_moment.start()
    time.sleep(60)
    # 执行 新客宝任务
    newPassengerTreasure = threading.Thread(target=newPassengerTreasure_selenium.newPassengerTreasure, args=())
    newPassengerTreasure.start()
    time.sleep(60)
    # 执行 新品推荐任务
    newProducts = threading.Thread(target=newProducts_selenium.newProducts, args=())
    newProducts.start()
    time.sleep(60)
    # 执行 潜客邀约任务
    invite_run = threading.Thread(target=invite_selenium.invite_run, args=())
    invite_run.start()
    time.sleep(60)
    # 执行 限时促销任务
    flashShale = threading.Thread(target=flashSale_selenium.flashShale, args=())
    flashShale.start()
    time.sleep(60)

def thirteen_zero():
    alibaba_visitor_marketing = threading.Thread(target=alibabaMarket.alibaba_visitor_marketing, args=())
    alibaba_visitor_marketing.start()
    time.sleep(60)

def five_zero():
    go = ProductCoupon()
    time.sleep(60)
    if go.create_new_products_coupon.date != date:
        create_new_products_coupon = threading.Thread(target=go.create_new_products_coupon, args=())
        create_new_products_coupon.start()
    if go.create_special_price_products_coupon.date != date:
        create_special_price_products_coupon = threading.Thread(target=go.create_special_price_products_coupon, args=())
        create_special_price_products_coupon.start()
    if go.delete_expire_product_coupons.date != date:
        delete_expire_product_coupons = threading.Thread(target=go.delete_expire_product_coupons, args=())
        delete_expire_product_coupons.start()



if __name__=="__main__":
    # 全天任务
    # 访客推送
    # os.system(r'start /b C:\"Program Files (x86)"\Python36-32\python.exe C:/Users/Administrator/Desktop/JAKCOM_DEV2/Project/Cn1688/visitorPush.py')

    # 轮询时间，间隔10秒
    while True:
        # 当前时间
        now = time.strftime('%H:%M')
        date = datetime.datetime.now().date()
        # 发放 越努力越幸运 定向优惠券
        if now == '09:00':
            nine_zero()

        # 创建 新品限时优惠 和 今日特价优惠 商品优惠券，删除 已结束 商品优惠券
        elif now == '00:05':
            zero_five()

        elif now == '00:10':
            zero_ten()

        # 执行 Alibaba 粉丝通任务
        elif now == '01:00':
            one_zero()

        # 执行 Alibaba 访客营销任务，美国时间0点刷新
        elif now == '13:00':
            thirteen_zero()

        elif now == '05:00':
            five_zero()
        else:
            print('正在执行 Python 本地定时任务，当前时间：%s ' % time.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(10)
            os.system("cls")

