# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: descriptionPageManager.py
@time: 2019/7/28 18:22
@desc: 描述页管理
"""
import re
import json
import requests
from aliexpressNew.public import Public


class DescriptionPageManager(Public):
    def __init__(self, account):
        self.account = account
        super(DescriptionPageManager, self).__init__(self.account)
        self.csrfToken = self.get_csrf_token()
        self.ctoken = self.get_ctoken()

    def setCookie(self):
        self.cookie = self.cookie + ';aep_common_f=eMDGONsKTvm7XmuxAkdzWk/SQrtl6Xj5SZVSbURyK712d7Ugy4bSbQ==;'
        self.headers['cookie'] = self.cookie

    def getModuleId(self):
        url = 'http://posting.aliexpress.com/wsproduct/detailmodule/ajaxModuleList.htm'
        data = 'status=approved&page=1&'
        # print(url)
        headers = self.headers
        # print(self.cookie)
        if 'aep_common_f' not in self.cookie:
            self.setCookie()
        response = requests.get(url, headers=headers)
        # print(response.text)
        itemData = {i['name']:i['id'] for i in response.json()['datas']}
        return itemData

    def getItem(self, name):
        if name == 'header':
            url = 'http://py1.jakcom.it:5000/aliexpress/post/product/mass_link_head'
            data = {
                'account': self.account
            }
            response = requests.post(url, data=data)
            itemDatas = re.findall(re.compile(r'<p><a .*?\shref="(.*?)">.*?\ssrc="(.*?)" /></a></p>', re.S),response.text)
            item = '<p>	<a href="{}"><img alt="a-c" src="{}"></a></p>'.format(itemDatas[0][0], itemDatas[0][1])
        else:
            url = 'http://py1.jakcom.it:5000/aliexpress/post/product/mass_link_end'
            data = {
                'account': self.account
            }
            response = requests.post(url, data=data)
            # print(response.text)
            # itemDatas = re.findall(re.compile(r'<a .*?\shref="(.*?)"><img alt="(.*?)" .*?\ssrc="(.*?)" /></a>', re.S), response.text)
            itemDatas = re.findall(re.compile(r'<body .*?>(.*?)</body>', re.S), response.text)[0]
            print(itemDatas)
            return itemDatas
            itemList = []
            for itemData in itemDatas:
                itemStr = '<a href="{}"><img alt="{}" src="{}"></a>'.format(itemData[0], itemData[1], itemData[2])
                itemList.append(itemStr)
            item = '<p>{}</p>'.format(' '.join(itemList))
        return item

    def submitItem(self, item):
        url = 'http://posting.aliexpress.com/wsproduct/detailmodule/editSelfModule.htm?moduleId=' + item['id']
        data = {
            '_csrf_token_': self.csrfToken,
            '_fmw.de._0.n': item['name'],
            '_fmw.de._0.m': item['value'],
            '_fmw.de._0.t': 'custom',
            '_fmw.de._0.i': item['id'],
            'action': 'detailmodule/detail_module_action',
            'event_submit_do_update': 'anything',
        }
        # print(data)
        response = requests.post(url, headers=self.headers, data=data, allow_redirects=False)
        print(response)
        if response.status_code == 302:
            self.sendLog({'account': self.account, 'type': item['name']})
            self.send_test_log(logName='描述页管理', logType='Run', msg='%s %s 设置成功' % (self.account, item['name']))
        else:
            self.send_test_log(logName='描述页管理', logType='Error', msg='%s %s 失败' % (self.account, item['name']))

    def sendLog(self, data):
        url = 'http://cs1.jakcom.it/AliexpressProductManage/update_descmodule_log'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)


    def main(self):
        # self.setCookie()
        itemData = self.getModuleId()
        # self.getItem('ender')
        for name, id in itemData.items():
            # if name == 'header':
            #     continue
            item = {
                'name': name,
                'value': self.getItem(name),
                'id': str(id)
            }
            self.submitItem(item)
            print('\n' * 5)


# 获取速卖通全部账号
def getAccount():
    url = 'http://py2.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def bug(logName, msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.160:90/Log/Write'
    data = {
        'LogName': logName,
        'LogType': 'Running Failed',
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)


def main():
    accountList = getAccount()
    for account in accountList:
        # account = 'fb2@jakcom.com'
        # if '1333' not in account:
        #     continue
        print('**' * 50)
        print(account)
        print('**' * 50)
        # descriptionPageManager = DescriptionPageManager(account)
        # descriptionPageManager.main()
        try:
            descriptionPageManager = DescriptionPageManager(account)
            descriptionPageManager.main()
        except Exception as e:
            pass
            print(e)
            # bug(logName='描述页管理', msg='%s %s' % (account, str(e)))


if __name__ == '__main__':
    main()