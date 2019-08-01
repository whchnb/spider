# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: microDynamic.py
@time: 2019/5/14 13:40
@desc: 每天00:10 定时发布微供动态
"""
import re
import json
import requests
import datetime
from DynamicAnnouncement.public import Public


class MicroDynamic(Public):

    # 类的初始化
    def __init__(self):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        super(MicroDynamic, self).__init__()
        # 获取token
        self.token = self.get_token(r"<input name='_csrf_token' type='hidden' value='(.*?)'>",
                                    'https://wg.1688.com/manage/feed/finish.htm?allowPush=1')

    # 获取图片
    def get_pic(self, sku):
        """
        获取图片
        :param sku: 需要获取图片的sku
        :return: 图片列表
        """
        # 获取图片的链接
        url = 'http://192.168.1.99:5000/1688/get/ablum_sku_wechat_photos/{}'.format(sku)
        response = requests.get(url)
        # 获取到的结果为str，将它们已',' 分隔，得到pic_list
        pic_list = response.text.split(',')
        # 返回图片列表
        return pic_list

    # 提交信息
    def submit(self, product):
        """
        提交信息
        :param product: 需要发送动态的商品
        """
        # 提交信息的目标链接
        url = 'https://wg.1688.com/manage/ajax/pubFeed.json'
        # 构造日期
        date = str(datetime.datetime.now().date()).replace('-', '')
        # 从product 中获取商品名
        product_name = product['product']['name']
        # 从product 中获取商品id
        product_id = product['product']['id']
        # 需要发布动态的内容
        description = """
        淘货源今日特价「%s期」
        %s 满50减10，满100减20，8折优惠，仅限今日！""" % (date, product_name)
        # 利用正则匹配sku 名称
        sku = re.findall(r'[a-zA-Z0-9]+', product_name)[0]
        # 获取sku 对应的pic_list
        pic_list = self.get_pic(sku)
        # 构造data，若发送的data 中键有同名的，则不能使用dict 发送，需要list + tuple 发送
        data = [
            ('_csrf_token', self.token),
            ('description', description.encode('gbk')),  # 带中文的参数需将其编码为浏览器对应编码，否则提交后数据乱码
            ('offerIds[]', int(product_id)),
            ('top', '0'),
            ('feedId', '0'),
            ('images[]', pic_list[0]),
            ('images[]', pic_list[1]),
            ('images[]', pic_list[2]),
            ('images[]', pic_list[3]),
            ('images[]', pic_list[4]),
            ('images[]', pic_list[5]),
            ('images[]', pic_list[6]),
            ('images[]', pic_list[7]),
            ('images[]', pic_list[8]),
            ('mediaType', '0'),
            ('allowPush', '1'),
        ]
        response = requests.post(url, data=data, headers=self.headers, verify=False)
        status = json.loads(response.text)['success']
        product_dict = [{'product': {'name': product_name, 'id': product_id}}]
        if status == True:
            self.send_log(channel='微供动态', products=product_dict, createtime=(datetime.datetime.now()))
            self.send_test_log(logName='微供动态', logType='Run', msg='发布成功 ' + response.text)
        else:
            self.send_test_log(logName='微供动态', logType='Error', msg='发布失败 ' + response.text)



if __name__ == '__main__':
    microDynamic = MicroDynamic()
    products = microDynamic.get_products()
    for product in products:
        microDynamic.submit(product)
