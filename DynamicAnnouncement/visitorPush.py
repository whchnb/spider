# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: visitorPush.py
@time: 2019/5/15 15:12
@desc: 访客推送

"""
import re
import time
import json
import datetime
import requests
import threading
from DynamicAnnouncement.public import Public


class VisitorPush(Public):

    # 类的初始化
    def __init__(self):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        super(VisitorPush, self).__init__()
        # 获取csrf_token
        self.csrf_token = self.get_csrf_token()
        print(self.csrf_token)
        # 构建时间
        self.t = str(time.time()).replace('.', '')[:13]
        # 获取已经推送过的客户列表
        self.buyer_already_push_list = self.get_already_push()

    # 获取csrf_token
    def get_csrf_token(self):
        """
        获取csrf_token
        :return: csrf_token
        """
        token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        csrf_token = re.findall(token_re_compile, self.cookie)[0]
        return csrf_token

    # 获取所有客户
    def get_all_buyer(self):
        """
        获取所有客户
        """
        # 添加请求头
        self.headers['referer'] = 'https://pm.1688.com/itrade/index/index.htm'
        # 获取所有客户的目标链接
        url = 'https://widget.1688.com/front/getJsonComponent.json?callback=jQuery183004045760352201633_{}&dmtrack_pageid=ddcc71460b15481715571562662983211260826619&namespace=getVisitorList&widgetId=getVisitorList&methodName=execute&params=%7B%22fromApp%22%3Afalse%2C%22isToday%22%3Atrue%2C%22pageNo%22%3A1%2C%22pageSize%22%3A10%7D&fromApp=false&isToday=true&pageNo=1&pageSize=10&_tb_token_={}&_={}'.format(self.t, self.csrf_token, self.t)
        response = requests.get(url, headers=self.headers, verify=False)
        data = json.loads(response.text[42:-1])
        visitors_data = data['content']['visitors']
        for visitor_data in visitors_data:
            # 获取客户姓名
            buyer_name = visitor_data['showName']
            # 获取客户id
            buyer_id = visitor_data['visitorId']
            # print(visitor_data['showName'], visitor_data['isBlack'], visitor_data['visitorId'], visitor_data['siteOnline'] )
            # 判断目标客户今天是否已经推送过
            if buyer_name not in self.buyer_already_push_list:
                print(buyer_id)
                # 推送
                self.submit(buyer_id)
            else:
                print('用户 {} id {} 今天已经推送过'.format(buyer_name, buyer_id))

    # 推送信息
    def submit(self, visitorId):
        """
        推送信息
        :param visitorId:  客户id
        """
        # 推送信息目标链接
        url = 'https://pm.1688.com/itrade/notification/notifyVisitor.json'
        parmars = {
            'uid':visitorId,
            'content': '全场现货，即拍即发；可OEM定制，无起订量限制不加价'.encode('gbk')
        }
        response = requests.get(url, params=parmars, headers=self.headers, verify=False)
        data = json.loads(response.text)
        try:
            # 发送成功
            if data['status'] == 'ok':
                visit_time, buyer_name = self.get_visit_time(visitorId)
                push_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
                # 写入日志
                self.log(buyerName=buyer_name, visit_time=visit_time, push_time=push_time)
        except Exception as e:
            self.send_test_log(logName='访客推送', logType='Error', msg=str(e))

    # 获取客户访问时间
    def get_visit_time(self, visitorId):
        """
        获取客户访问时间
        :param visitorId: 客户id
        :return: 访问时间，客户姓名
        """
        url = 'https://widget.1688.com/front/getJsonComponent.json'
        params = {
            'callback': 'jQuery183008330973135485098_{}'.format(self.t),
            'dmtrack_pageid': 'ddcc71460b0b762c15571794250889314005357937',
            'namespace': 'getVisitorBaseInfo',
            'widgetId': 'getVisitorBaseInfo',
            'methodName': 'execute',
            'params': {
                "visitorId":visitorId
            },
            'visitorId': visitorId,
            '_tb_token_': self.csrf_token,
            '_': '{}'.format(self.t),
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        data = json.loads(response.text[42:-1])
        # 获取访问时间，时间戳
        accessTime = data['content']['visitorBaseInfo']['accessTime']
        # 构造访问时间
        visit_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(str(accessTime)[:10])))
        buyer_name = data['content']['visitorBaseInfo']['showName']
        # 返回访问时间，客户姓名
        return visit_time, buyer_name

    # 日志
    def log(self, buyerName, visit_time, push_time):
        """
        日式
        :param buyerName: 客户姓名
        :param visit_time: 访问时间
        :param push_time: 推送信息时间
        """
        url = 'http://192.168.1.99:90/OSEE/visitor_pushlog'
        data = {
            'Account': 'jakcomcom',
            'buyername': buyerName,
            'visit_time': visit_time,
            'push_time': push_time
        }
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    # 获取已经推送过信息的客户
    def get_already_push(self):
        """
        获取已经推送过信息的客户
        :return: 已经推送过信息的客户列表
        """
        url = 'http://192.168.1.99:90/OSEE/get_visitorpushlog'
        params = {
            'Account': 'jakcomcom',
        }
        response = requests.get(url, params=params)
        buyer_datas = json.loads(response.text)['data']
        buyer_list = [i['buyername'] for i in buyer_datas]
        # 返回已经推送过信息的客户列表
        return buyer_list


def send_test_log(logName,logType, msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.99:90/Log/Write'
    data = {
        'LogName': logName,
        'LogType': logType,
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)

def main():
    try:
        visitor = VisitorPush()
        print('start')
        # 实例化对象
        visitor.get_all_buyer()
        print('done')
        print(datetime.datetime.now())
        # 开启线程，10 秒钟查询发送一次
        threading.Timer(10.0, main).start()
    except Exception as e:
        print('出错了', e)
        send_test_log(logName='访客推送', logType='Error', msg=str(e))
        time.sleep(60)
        return main()


if __name__ == '__main__':
    main()
