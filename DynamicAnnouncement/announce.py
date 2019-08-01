# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: announce.py
@time: 2019/5/14 12:50
@desc: 每天00:10 定时发布公告（淘货源公告）
"""
import json
import datetime
import requests
from DynamicAnnouncement.public import Public


class Announce(Public):

    # 类的初始化
    def __init__(self):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        super(Announce,self).__init__()
        # 获取token
        self.token = self.get_token(r'<input type="hidden" name="_csrf" value="(.*?)"/>', 'https://channel.1688.com/page/bulletinpublish.htm')
        # 获取淘货源公告今日所需要发布的内容
        self.content = self.get_content()['tao_huo_yuan']
        self.products = self.get_products()

    # 提交信息
    def submit(self):
        """
        提交信息
        """
        # 提交信息的链接
        submit_url = 'https://channel.1688.com/event/app/newchannel_gy_bulletin/saveBulletin.htm'
        # 构造标题
        title = '淘货源今日特价「{}期」'.format(str(datetime.datetime.now().date()).replace('-', ''))
        # 构造表单数据
        data = {
            'id': '',
            'headline': title.encode('gbk'),        # 带中文的参数需将其编码为浏览器对应编码，否则提交后数据乱码
            'content': self.content.encode('gbk'),  # 带中文的参数需将其编码为浏览器对应编码，否则提交后数据乱码
            '_csrf_token': self.token,
            '_input_charset': 'utf8',
        }
        response = requests.post(submit_url, data=data, headers=self.headers, verify=False)
        # 从返回的响应中获取状态码
        status = json.loads(response.text)['result']['isSuccess']
        if status is True:
            self.send_log(channel='淘货源公告', products=self.products, createtime=(datetime.datetime.now()))
            self.send_test_log(logName='淘货源公告', logType='Run', msg='发布成功 ' + response.text)
        else:
            self.send_test_log(logName='淘货源公告', logType='Error', msg='发布失败 '+ response.text)

if __name__ == '__main__':
    announce = Announce()
    announce.submit()