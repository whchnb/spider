# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: storeConstruction.py
@time: 2019/6/13 11:53
@desc:  速卖通店铺装修
"""
import re
import json
import urllib3
import datetime
import requests
from urllib.parse import urlencode
from aliExpress.public import Public

urllib3.disable_warnings()


class StoreConstruction(Public):
    def __init__(self, account, clientType):
        self.account = account
        super(StoreConstruction, self).__init__(self.account)
        self.clientType = clientType
        self.csrf_token = self.get_c_token()
        self.pageId = self.get_pageId()
        self.index = 0

    # 获取商品
    def get_products(self):
        url = 'http://cs1.jakcom.it/Aliexpress_storemanage/getproducts_hotsale?account=%s' % self.account
        response = requests.get(url)
        datas = response.json()
        return datas

    # 获取页面id
    def get_pageId(self):
        url = 'https://siteadmin.aliexpress.com/page/getPageList'
        pageTypeId = 15 if self.clientType != 'pc' else 28
        params = {
            'clientType': self.clientType,
            'csrf_token': self.csrf_token,
            'currentPageName': '首页',
            'currentPage': '1',
            'pageSize': '10',
            'pageTypeId': pageTypeId,
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        pageId_datas = response.json()['result']['data']['pageList']
        for pageId_data in pageId_datas:
            if pageId_data['pageName'] == 'Homepage':
                print(pageId_data['pageId'])
                return pageId_data['pageId']

    # 获取csrf_token
    def get_c_token(self):
        url = 'https://siteadmin.aliexpress.com'
        response = requests.get(url, headers=self.headers, verify=False)
        c_token_re_compile = re.compile(r"<input name='csrf_token' type='hidden' value=(.*?)>", re.S)
        c_token = re.findall(c_token_re_compile, response.text)[0]
        return c_token

    # 获取新的cookie
    def get_new_cookie(self):
        url = 'https://siteadmin.aliexpress.com/finder/api/folders'
        response = requests.get(url, headers=self.headers, verify=False)
        cookie_response = response.headers.get('Set-Cookie', 'set-cookie')
        data_re_compile = re.compile(r'AMSSESSIONID=(.*?);.*?AMSSESSIONID\.sig=(.*?);', re.S)
        data = re.findall(data_re_compile, cookie_response)[0]
        self.cookie = self.cookie + '; AMSSESSIONID=%s; AMSSESSIONID.sig=%s' % (data[0], data[1])
        self.headers['cookie'] = self.cookie

    # 获取csrf
    def get_csrf(self):
        url = 'https://siteadmin.aliexpress.com/finder/upload'
        response = requests.get(url, headers=self.headers, verify=False)
        csrf_re_compile = re.compile(r'<input type="hidden" id="_csrf" value="(.*?)">', re.S)
        csrf = re.findall(csrf_re_compile, response.text)[0]
        # print(csrf)
        return csrf

    # 获取每栏的id
    def get_column_id(self):
        url = 'https://siteadmin.aliexpress.com/%s/getEditorPageData' % self.clientType
        params = {
            'clientType': self.clientType,
            'pageId': self.pageId,
            'csrf_token': self.csrf_token
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)

        if self.clientType == 'pc':
            self.shopId = response.json()['result']['pageData']['globalData']['shopId']
            column_datas = response.json()['result']['pageData']['components']
            for widgetId, column_data in column_datas.items():
                moduleTitle = column_data['moduleTitle']
                if moduleTitle in ['满件折', '单列图文', '轮播图', '产品列表', '热区图片', '文本模块']:
                    # pass
                    self.remove_column(widgetId)
                # sys.exit()
        else:
            column_datas = response.json()['result']['moduleList']
            self.shopId = response.json()['result']['globalData']['shopId']
            for column_data in column_datas:
                moduleTitle = column_data['moduleTitle']
                if moduleTitle in ['满件折', '单列图文', '轮播图', '产品列表', '热区图片', '文本模块']:
                    # pass
                    self.remove_column(column_data['widgetId'])
                # sys.exit()

    # 删除栏
    def remove_column(self, widgetId):
        print('移除栏位')
        url = 'https://siteadmin.aliexpress.com/%s/removeModule' % self.clientType
        params = {
            'clientType': self.clientType,
            'pageId': self.pageId,
            'areaType': 'bd',
            'widgetId': widgetId,
            # 'csrf_token': '4b275510-67ed-4d12-8ae9-4c9d41cd8ed5',
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        print(response.text)

    # 添加图片
    def add_img(self, img_data):
        url = 'https://kfupload.alibaba.com/mupload'
        img_name = img_data[0]
        img_path = img_data[1]
        fireFox_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Host": "kfupload.alibaba.com",
            "Origin": "https://siteadmin.aliexpress.com",
            "Pragma": "no-cache",
            "Referer": "https://siteadmin.aliexpress.com/finder/upload?single=true&folder=temp&compress=false&clip=false&theme=green&uploadedClose=false&origin=https%3A%2F%2Fsiteadmin.aliexpress.com&random=0.28051166147738504&cacheLength=1&extensions=&maxSize=",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0",
        }
        http = urllib3.PoolManager()
        response = http.request(
            'POST',
            url,
            headers=fireFox_headers,
            multipart_boundary='----WebKitFormBoundaryFQ3F3vu7DyVZwuob',
            fields={
                'file': (img_name, open(img_path, 'rb').read(), 'image/jpeg'),
                'name': (None, 'jwu7oxap.jpg', None),
                'scene': (None, 'aeAmsPicUploaderNsRule', None),
            }
        )
        text = response.data.decode("UTF-8")
        set_up_data = json.loads(text)
        set_up_data = {
            **set_up_data,
            **{
                'img_name': img_name
            }
        }
        return set_up_data

    # 引用图片
    def upload_img(self, set_up_data):
        print('上传图片')
        csrf = self.get_csrf()
        img_name = set_up_data['img_name']
        img_size = set_up_data['size']
        img_url = set_up_data['url']
        img_hash = set_up_data['hash']
        img_width = set_up_data['width']
        img_height = set_up_data['height']
        url = 'https://siteadmin.aliexpress.com/finder/api/files'
        data = {
            'files[0][id]': 'jwu7oxap',
            'files[0][name]': img_name,
            'files[0][size]': img_size,
            'files[0][bytes]': img_size,
            'files[0][url]': img_url,
            'files[0][key]': img_hash,
            'files[0][width]': img_width,
            'files[0][height]': img_height,
            'files[0][folder_id]': 'temp',
            'confirmation': True,
            '_csrf': csrf,
        }
        headers = self.headers
        headers['accept'] = 'application/json, text/javascript, */*; q=0.01'
        response = requests.post(url, data=data, headers=headers, verify=False)
        return response.json()

    # 添加店招
    def add_shop_trick(self):
        img_name = 'PC.jpg' if self.clientType == 'pc' else 'MB.jpg'
        img_path = r'\\192.168.1.98\公共共享盘\3_美工素材\1 店铺装修图\aliexpress\店招' + r'\%s' % img_name
        img_data = (img_name, img_path)
        print('添加店招图片')
        set_up_data = self.add_img(img_data)
        self.upload_img(set_up_data)

    # 添加栏位
    def add_column(self, product_data):
        print('添加栏位')
        if self.clientType == 'pc':
            url = 'https://siteadmin.aliexpress.com/%s/addLayout' % self.clientType
            params = {
                'clientType': self.clientType,
                'pageId': self.pageId,
                'layoutIndex': '0',
                'gridIndex': '0',
                'moduleIndex': '0',
                'componentKey': 'singleImageText',
                'layoutStyle': 'AE_F1200',
                'csrf_token': self.csrf_token
            }
        else:
            url = 'https://siteadmin.aliexpress.com/%s/addModule' % self.clientType
            params = {
                'clientType': self.clientType,
                'pageId': self.pageId,
                'componentKey': 'singleImageText',
                'index': 0,
                'csrf_token': self.csrf_token
            }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        print(response)
        widgetId = response.json()['result']['widgetId']
        # url = 'https://siteadmin.aliexpress.com/editor/previewModule?clientType=%s&' % self.clientType
        url = 'https://siteadmin.aliexpress.com/editor/saveModule?clientType=%s&' % self.clientType
        self.add_column_img(url, product_data, widgetId)


    # 添加栏位图片
    def add_column_img(self, url, product_data, widgetId):
        sku = product_data['SKU']
        product_id = product_data['Product_ID']
        img_name = '%s.jpg' % sku
        clientCode = 1920 if self.clientType == 'pc' else 750
        img_path = r'\\192.168.1.98\公共共享盘\3_美工素材\1 店铺装修图\aliexpress\%s-SKU' % clientCode + r'\%s' % img_name
        print('添加栏位图片')
        content = product_data['Title'] if self.clientType == 'pc' else ''
        title = product_data['Title']
        link = '//www.aliexpress.com/store/product/%s/%s_%s.html' % (title, self.shopId, product_id)
        img_data = (img_name, img_path)
        set_up_data = self.add_img(img_data)
        img_datas = self.upload_img(set_up_data)
        img_text_link = {
            "hideBottom": True,
            "text": content,
            "link": link,
            "image": {
                "url": set_up_data['url'],
                "width": int(set_up_data['width']),
                "height": int(set_up_data['height'])
            }
        }
        languages = ['Polish', 'Vietnamese', 'German', 'Indonesian', 'Arabic', 'Italian', 'Dutch', 'Spanish',
                     'Ukrainian', 'Hebrew', 'French', 'Japanese', 'Thai', 'Russian', 'English', 'Portuguese', 'Turkish',
                     'Korean']
        moduleData = {language: img_text_link for language in languages}
        text = {language: content for language in languages}
        url_dict = {language: set_up_data['url'] for language in languages}
        data = {
            'pageId': int(self.pageId),
            'moduleData': json.dumps(moduleData),
            'validData': json.dumps({
                'hideBottom': True,
                'text': text,
                'link': link,
                'image': {
                    'url': url_dict,
                    "width": int(set_up_data['width']),
                    "height": int(set_up_data['height'])
                }
            }),
            'widgetId': int(widgetId),
            'csrf_token': self.csrf_token
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, data=data, headers=headers, verify=False)
        print(response)
        print(response.json())


    # 获取所有的sku
    def get_all_sku(self):
        url = 'http://cs1.jakcom.it/alibaba/skulist'
        response = requests.get(url)
        return response.json()

    # 添加满减折
    def add_full_discount(self):
        print('添加满减折')
        if self.clientType == 'pc':
            url = 'https://siteadmin.aliexpress.com/%s/addLayout' % self.clientType
            params = {
                'clientType': self.clientType,
                'pageId': self.pageId,
                'layoutIndex': '13',
                'gridIndex': '0',
                'moduleIndex': '0',
                'componentKey': 'fullPieceDiscountPromo',
                'layoutStyle': 'AE_F1200',
                'csrf_token': self.csrf_token
            }
        else:
            url = 'https://siteadmin.aliexpress.com/%s/addModule' % self.clientType
            params = {
                'clientType': self.clientType,
                'pageId': self.pageId,
                'componentKey': 'fullPieceDiscountPromo',
                'index': self.index,
                'csrf_token': self.csrf_token
            }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        print(response)
        print(response.text)

    # 发布
    def submit(self):
        print('发布')
        url = 'https://siteadmin.aliexpress.com/editor/batchSaveModule?clientType=%s&' % self.clientType
        data = {
            'pageId':self.pageId,
            'moduleList': [],
            'csrf_token': self.csrf_token
        }
        headers = self.headers
        headers['cookie'] = self.cookie
        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)

    # 获取跳转链接
    def get_link(self):
        print('获取链接')
        url = 'https://siteadmin.aliexpress.com/editor/publishPage'
        params = {
            'clientType': self.clientType,
            'pageId': self.pageId,
            'setViewDefault':False,
            'csrf_token': self.csrf_token
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        print(response)
        Store_url = response.json()['result']['longUrl']
        return Store_url

    def send_log(self, Store_url):
        url = 'http://cs1.jakcom.it/Aliexpress_storemanage/dstoredecoration_save'
        data = {
            'Account': self.account,
            'Store_url': Store_url,
            'Decoration_lasttime': str(datetime.datetime.now().date()),
            'Decoration_state': '装修完毕,已发布'
        }
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    # 主方法
    def main(self):
        # print(111)
        self.get_new_cookie()
        self.get_column_id()
        self.add_shop_trick()
        product_datas = self.get_products()
        sku_list = self.get_all_sku()
        for product_data in product_datas:
            sku = product_data['SKU']
            if sku not in sku_list or sku == 'P2':
                continue
            print(product_data)
            self.index += 1
            self.add_column(product_data)
        self.add_full_discount()
        self.submit()
        Store_url = self.get_link()
        self.send_log(Store_url)


def main(account):
    clientTypes = [
        'pc',
        # 'wireless'
    ]
    for clientType in clientTypes:
        storeConstruction = StoreConstruction(account, clientType)
        storeConstruction.main()


if __name__ == '__main__':
    account = 'fb2@jakcom.com'
    main(account)
