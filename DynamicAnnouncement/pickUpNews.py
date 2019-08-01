# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: pickUpNews.py
@time: 2019/5/14 15:14
@desc:
"""
import re
import time
import json
import datetime
import requests
from DynamicAnnouncement.public import Public


class PickUpNews(Public):

    def __init__(self):
        super(PickUpNews, self).__init__()


    def get_csrf_token(self):
        token_re_compile = re.compile(r'_tb_token_=(.*?);', re.S)
        csrf_token = re.findall(token_re_compile, self.cookie)[0]
        return csrf_token

    def submit(self):
        # headers = {
        #     'authority': 'channel.1688.com',
        #     # 'method': 'GET',
        #     'path': '/page/bulletinpublish.htm',
        #     'scheme': 'https',
        #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        #     # 'cookie': 'UM_distinctid=16a8b52b22d7d-059d3153703b06-e323069-1fa400-16a8b52b22e3a3; cna=n4lWFZbRW2YCAbe/sh4Lxj33; ali_apache_id=11.186.201.38.1557135135792.051504.0; cookie2=193f6dd5e40b25c1ef98bcfdbc836cb7; t=1f71f19a13a626847bf3376cbfa1cbe0; _tb_token_=e3bd6eb8ba075; ali_apache_tracktmp=c_w_signed=Y; __rn_alert__=false; cookie1=BxoD8yON%2BLKP2nR%2FU%2BsuODsyQQ7FVtqL2homXzhyRFg%3D; cookie17=UUpkv67HfD0F4g%3D%3D; sg=m53; csg=4dbf97fe; lid=jakcomcom; unb=2257499635; __cn_logon__=true; __cn_logon_id__=jakcomcom; ali_apache_track=c_mid=b2b-2257499635|c_lid=jakcomcom|c_ms=2|c_mt=2; _nk_=jakcomcom; last_mid=b2b-2257499635; _csrf_token=1557806449090; ctoken=uyVSFXrNcxM719IOgDU7coco; ali-ss=eyJtZW1iZXJJZCI6ImIyYi0yMjU3NDk5NjM1IiwidXNlcklkIjoyMjU3NDk5NjM1LCJsb2dpbklkIjoiamFrY29tY29tIiwic2lkIjoiMTkzZjZkZDVlNDBiMjVjMWVmOThiY2ZkYmM4MzZjYjciLCJlY29kZSI6IiIsImxvZ2luU3RhdHVzUmV0TXNnIjpudWxsLCJsb2dpbk1lc3NhZ2VFcnJvciI6bnVsbCwibG9naW5FcnJvclVzZXJOYW1lIjpudWxsLCJjaGVja2NvZGUiOm51bGwsIl9leHBpcmUiOjE1NTc4OTM0NTI4NTIsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; _is_show_loginId_change_block_=b2b-2257499635_false; _show_force_unbind_div_=b2b-2257499635_false; _show_sys_unbind_div_=b2b-2257499635_false; _show_user_unbind_div_=b2b-2257499635_false; alicnweb=touch_tb_at%3D1557820013851%7Clastlogonid%3Djakcomcom%7Cshow_inter_tips%3Dfalse; __mbox_csrf_token=4R8htFuCp794wOX5_1557824300242; l=bBM41yPPvD94RYn2BOfNCuI8LS7OgQRf1sPzw4OgiICPO_WM5mhNWZ9N4BKHC3GVa6cp5387PXqQBAYEvyznh; isg=BFVVlpjwpU4_94EnuNs_6ZA0ZFHP-gjkW4YB8tf4jkwbLnYgm6P9Nams-HI9LiEc',
        #     'cookie': self.cookie,
        #     'Origin': 'https://widget.1688.com',
        #     'referer': 'https://widget.1688.com/front/ajax/bridge.html',
        #     # 'upgrade-insecure-requests': '1',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        # }
        url = 'https://widget.1688.com/front/ajax/getJsonComponent.json'
        date = str(datetime.datetime.now().date()).replace('-', '')
        products = self.get_products()
        content = []
        for index, product in enumerate(products):
            product_id = product['product']['id']
            print(product_id)  # 589083283714
            offerUrl = "https://detail.1688.com/offer/{}.html".format(product_id)
            imageUrl, offerTitle, price = self.get_img_price(offerUrl)
            product_contennt = {"type": "offer", "offerId": int(product_id),
                                "offerUrl": offerUrl,
                                "imageUrl": imageUrl,
                                "offerTitle": offerTitle, "unitPrice": price,
                                "order": index}
            content.append(product_contennt)
        data = {
            'status': 'published',
            'feedType': 'offerlist',
            'content': str(content),
            'tellToBuyerDesc': '今日特价「{}期」，全天八折优惠，满50减10，满100减20。'.format(date),
            'topicId': None,
            'title': '今日特价「{}期」'.format(date),
        }
        formData = {
            'namespace': 'saveTiaohuoFeed',
            'widgetId': 'saveTiaohuoFeed',
            'methodName': 'execute',
            'params': str(data),
            'status': 'published',
            'feedType': 'offerlist',
            'content': str(content),
            'tellToBuyerDesc': '今日特价「{}期」，全天八折优惠，满50减10，满100减20。'.format(date),
            'topicId': '',
            'title': '今日特价「{}期」'.format(date),
            # '__mbox_csrf_token': self.csrf_token + '_{}'.format(str(time.time()).replace('.', '')[:13]),
            '__mbox_csrf_token': self.get_csrf_token(),
        }
        print(formData)
        response = requests.post(url, headers=self.headers, data=formData)
        print(response)
        print(response.headers)
        print(response.reason)
        print(response.text)

    def get_img_price(self, url):
        response = requests.get(url, headers=self.headers)
        re_str = '<a class="box-img".*?hidefocus="true">.*?<img src="(.*?)" alt="(.*?)"/>'
        data_re_complie = re.compile(re_str, re.S)
        data = re.findall(data_re_complie, response.text)[0]
        imageUrl, offerTitle = data
        image_list = imageUrl.split('.')
        image_list [-2] = '120x120'
        imageUrl = '.'.join(image_list)
        print(imageUrl)
        price = re.findall(re.compile(r'"begin":"1000","end":"","price":"(.*?)"', re.S), response.text)[0]
        return imageUrl, offerTitle, price


if __name__ == '__main__':
    pickUpNews = PickUpNews()
    pickUpNews.submit()
