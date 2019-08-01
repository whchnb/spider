# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: emptyRecycleBin.py
@time: 2019/6/27 16:15
@desc: 清空回收站
"""
import re
import requests
from alibaba.public import Public


class EmptyRecycleBin(Public):
    def __init__(self, account):
        self.account = account
        super(EmptyRecycleBin, self).__init__(self.account)

    def getCsrfToken(self):
        url = 'https://hz-productposting.alibaba.com/trash/trash_manage.htm'
        respose = requests.get(url, headers=self.headers)
        csrfToken = re.findall(re.compile(r"<input name='_csrf_token_' type='hidden' value='(.*?)'>", re.S), respose.text)[0]
        return csrfToken

    def empty(self):
        url = 'https://hz-productposting.alibaba.com/trash/trash_manage.htm'
        csrfToken = self.getCsrfToken()
        data = {
            'action': 'trash_manage_action',
            'event_submit_do_delete': '',
            'event_submit_do_clear': 'anything',
            'event_submit_do_recover': '',
            'trashType': 'product',
            'id': '',
            'origin': '',
            '_csrf_token_': csrfToken,
        }
        self.headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, data=data, headers=self.headers)
        if response.status_code == 200:
            return True

    def main(self):
        msg = self.empty()
        return msg

def main(account):
    emptyRecycleBin = EmptyRecycleBin(account)
    msg = emptyRecycleBin.main()
    return msg


if __name__ == '__main__':
    account = 'fb2@jakcom.com'
    main(account)