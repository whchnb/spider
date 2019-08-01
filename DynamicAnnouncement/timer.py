"""
本地任务定时器

"""

# 导入自制模块
from Cn1688.product_coupon import ProductCoupon
from Cn1688.target_coupon import TargetCoupon
from Cn1688.visitorPush import visitor_push
from Cn1688 import announce, distribution, microDynamic
from Cn1688 import newPassengerTreasure_selenium, newProducts_selenium, pickUpNews_with_selenium
from Alibaba import alibabaFan_with_selenium
from Alibaba import alibabaMarket

# 导入系统模块
import os
import time
import threading


if __name__=="__main__":
    # 全天任务
    # 访客推送
    visitor_push = threading.Thread(target=visitor_push, args=())
    visitor_push.start()

    # 轮询时间，间隔10秒
    while True:
        # 当前时间
        now = time.strftime('%H:%M')

        # 发放 越努力越幸运 定向优惠券
        if now == '09:00':
            # 发放 越努力越幸运 定向优惠券
            go = TargetCoupon()
            go.send_lucky_coupon()
            time.sleep(60)

        # 创建 新品限时优惠 和 今日特价优惠 商品优惠券，删除 已结束 商品优惠券
        elif now == '00:05':
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

        elif now == '00:10':
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

        # 执行 Alibaba 粉丝通任务
        elif now == '01:00':
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






        # 执行 Alibaba 访客营销任务，美国时间0点刷新
        elif now == '13:00':
            alibaba_visitor_marketing = threading.Thread(target=alibabaMarket.alibaba_visitor_marketing, args=())
            alibaba_visitor_marketing.start()
            time.sleep(60)

        else:
            print('正在执行 Python 本地定时任务，当前时间：%s ' % time.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(10)
            os.system("cls")

