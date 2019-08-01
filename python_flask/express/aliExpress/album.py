# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: album.py
@time: 2019/5/27 17:42
@desc:
"""
import os
import ssl
import time
import json
import urllib3
import requests
from aliExpress.public import Public

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

class Album(Public):

    def __init__(self, account):
        self.account = account
        super(Album, self).__init__(account)
        self.ctoken = self.get_ctoken()

    # 获取本地相册信息
    def get_local_album(self):
        print('正在获取本地相册信息')
        local_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Aliexpress'
        files = os.listdir(local_path)
        albums_dict = {}
        for file in files:
            albums_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Aliexpress\{}'.format(file)
            albums = os.listdir(albums_path)
            album_list = []
            for album in albums:
                album_path = albums_path + '\\' + album
                album_dict = {
                    'name': album,
                    'date': str(os.path.getmtime(album_path)).replace('.', '')[:13]
                }
                album_list.append(album_dict)
            albums_dict[file] = album_list
        return albums_dict

    # 获取网络相册信息
    def get_online_album(self):
        print('正在获取网络相册信息')
        url = 'http://photobank.aliexpress.com/photobank/ajaxImageGroup.htm'
        params = {
            'levelCode': ',,',
            'event': 'listSubGroups',
            'topLevel': 'true',
            'ctoken': self.ctoken,
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        datas = json.loads(response.text)
        online_album_detail = []
        print('获取网上照片信息')
        for data in datas:
            online_album = {}
            album_id = data['node']['value']
            sku = data['node']['text']
            photo_list = self.get_photo(album_id, self.ctoken, sku, photo_list=[])
            online_album['album_name'] = sku
            online_album['album_id'] = album_id
            online_album['photo_list'] = photo_list
            online_album_detail.append(online_album)
        return online_album_detail

    # 获取网上照片信息
    def get_photo(self, album_id, ctoken, sku, page=1, photo_list=[]):
        url = 'http://photobank.aliexpress.com/photobank/ajaxPhotobank.htm?ctoken={}'.format(ctoken)
        data = {
            'groupId': str(album_id),
            'event': 'searchImage',
            'location': 'subGroup',
            'page': page
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        response = requests.post(url, headers=headers, data=data, verify=False)
        datas = json.loads(response.text)
        try:
            photo_datas = datas['imageInfos']
        except Exception as e:
            print(e)
            print(datas)
            status = datas['success']
            time.sleep(2)
            self.get_photo(album_id, ctoken, sku, page, photo_list)
        last_page = datas['query']['totalPage']
        if page <= last_page:
            for photo_data in photo_datas:
                photo_dict = {}
                photo_dict['name'] = photo_data['displayName']['value']
                photo_dict['fileName'] = photo_data['fileName']
                photo_dict['id'] = photo_data['id']
                photo_dict['url'] = photo_data['url']
                photo_dict['createTime'] = photo_data['gmtCreate']['time']
                reference = photo_data['referenceCount']
                photo_dict['referenceCount'] = '已引用' if int(reference) != 0 else '未引用'
                photo_list.append(photo_dict)
            page += 1
            return self.get_photo(album_id, ctoken, sku, page, photo_list)
        else:
            return photo_list

    # 更新网络图片
    def update(self, local_album_detail, online_album_detail):
        print('正在更新网络图片')
        online_album_groups = {i['album_name']:[i['album_id'],i['photo_list']] for i in online_album_detail}
        for local_album_data in local_album_detail.keys():
            album_id = online_album_groups[local_album_data][0]
            online_album_photo_list = online_album_groups[local_album_data][1]
            local_photo_dict = {photo['name'].split('.')[0]: photo['date'] for photo in local_album_detail[local_album_data]}
            online_photo_dict = {photo['name']: photo['createTime'] for photo in online_album_photo_list}
            for name, create_time in local_photo_dict.items():
                if name not in online_photo_dict.keys():
                    print('{}不存在，正在上传'.format(name))
                    self.get_update_photo_data(local_album_data, name, album_id)
                elif int(create_time) > online_photo_dict[name]:
                    print('{}正在更新'.format(name))
                    self.get_update_photo_data(local_album_data, name, album_id)
            time.sleep(2)

    # 获取上传图片数据
    def get_update_photo_data(self, sku, new_photo, album_id):
        print('正在获取上传图片数据')
        set_up_url = 'https://kfupload.alibaba.com/mupload'
        new_photo_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Aliexpress\{}\{}.jpg'.format(sku, new_photo)
        file_name = new_photo + '.jpg'
        fireFox_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Host": "kfupload.alibaba.com",
            "Origin": "http://photobank.aliexpress.com",
            "Pragma": "no-cache",
            "Referer": "http://photobank.aliexpress.com/photobank/uploader-new.htm?watermark=Store%20No:%202742003",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0",
        }
        http = urllib3.PoolManager()
        set_up_response = http.request(
            'POST',
            set_up_url,
            # headers=self.headers,
            headers=fireFox_headers,
            multipart_boundary='----WebKitFormBoundaryNdURC56FeUZ5cBuv',
            fields={
                'file': (file_name, open(new_photo_path, 'rb').read(), 'image/jpeg'),
                'name': (None, 'jw8nlvrj.jpg', None),
                'scene': (None, 'aePhotobankImageNsRule', None),
            }
        )
        text = set_up_response.data.decode("UTF-8")
        set_up_data = json.loads(text)
        status = set_up_data['code']
        if status == '0':
            self.upload_photo(set_up_data, file_name, album_id)

    # 上传图片
    def upload_photo(self, set_up_data, file_name, album_id):
        print('正在上传图片')
        fileSavePath = set_up_data['fs_url']
        fileURL = set_up_data['url']
        fileName = file_name
        fileSize = set_up_data['size']
        fileHeight = set_up_data['height']
        fileWidth = set_up_data['width']
        fileMd5 = set_up_data['hash']
        csrf_token = self.get_csrf_token()
        upload_url = 'http://photobank.aliexpress.com/photobank/ajaxPhotobank.htm?_csrf_token_={}'.format(csrf_token)
        data = {
            'event': 'uploadImage',
            'imageFiles': 'fileId:0|fileSavePath:{}|fileURL:{}|fileName:{}|fileSize:{}|fileHeight:{}|fileWidth:{}|fileDestOrder:0|fileSrcOrder:0|fileFlag:add|isError:false|fileMd5:{}'.format(
                fileSavePath, fileURL, fileName, fileSize, fileHeight, fileWidth, fileMd5),
            'watermark': '',
            'groupId': album_id,
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        response = requests.post(url=upload_url, data=data, headers=headers, verify=False)
        print(response.text)

    # 创建分组
    def create_new_album_group(self, difference_groups):
        for sku in difference_groups:
            print('正在创建{}分组'.format(sku))
            url = 'http://photobank.aliexpress.com/photobank/ajaxImageGroup.htm?ctoken={}'.format(self.ctoken)
            data = {
                'newName': sku,
                'topLevel': True,
                'levelCode': ',,',
                '_t': int(str(time.time()).replace('.', '')[:13]),
                'event': 'addImageGroup',
            }
            headers = self.headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            response = requests.post(url, headers=headers, data=data, verify=False)
            data = json.loads(response.text)
            status = data['success']
            if status == 'true':
                print('相册分组{} 创建成功'.format(sku))
            else:
                print(data['errorMessage'])

    def log(self, datas):
        url = 'http://cs1.jakcom.it/Aliexpress_storemanage/Albuminfo_save'
        for data in datas:
            album_name = data['album_name']
            album_ID = data['album_id']
            Account = self.account
            for photo in data['photo_list']:
                image_name = photo['name']
                image_ID = photo['id']
                whether_reference = photo['referenceCount']
                img_url = photo['url']
                date = str(photo['createTime'])[:10] + '.' + str(photo['createTime'])[10:]
                filename = photo['fileName']
                statDate = time.localtime(float(date))
                createTime = time.strftime("%Y-%m-%d %H:%M:%S", statDate)
                Uptime = createTime
                data = {
                    'album_name': album_name,
                    'album_ID': album_ID,
                    'Account': Account,
                    'image_name': image_name,
                    'image_ID': image_ID,
                    'whether_reference': whether_reference,
                    'img_url': img_url,
                    'Uptime': Uptime,
                    'filename': filename
                }
                response = requests.post(url, data=data)
                print(response)
                print(response.text)
                print(data)

    def main(self):
        local_album_detail = self.get_local_album()
        online_album_detail = self.get_online_album()
        online_album_groups = {i['album_name']: [i['album_id'], i['photo_list']] for i in online_album_detail}
        difference_groups = list(set(local_album_detail.keys()).difference(online_album_groups.keys()))
        if len(difference_groups) != 0:
            self.create_new_album_group(difference_groups)
        online_album_detail = self.get_online_album()
        self.update(local_album_detail, online_album_detail)
        self.log(online_album_detail)


def main():
    account_list = [
        # 'fb1@jakcom.com',
        'fb2@jakcom.com',
        # 'fb3@jakcom.com',
        # 'tx@jakcom.com',
    ]
    for account in account_list:
        album = Album(account)
        album.main()


if __name__ == '__main__':
    main()
'cna=EAlbFYS29iYCAbe/sh4vRllm;l=bBLykegmvVxK73BQBOCaZuI8LoQOSIOYYuPRwCYHi_5BZ6L6Cj7OlH4j_Fp6Vs5RsnTB4wvOR4J9-etkj;isg=BFpa8xcd0roe-F4lmnUvacMIqAC8I98hkmjILGTTBu241_oRTBsudSAto2NuHFb9;ali_apache_id=10.103.166.17.1557404497831.588371.0;xman_us_f=x_l=1;x_locale=en_US;no_popup_today=n;x_user=CN|Jakcom|Technology|cnfm|230163491;zero_order=y;last_popup_time=1557404550002;xman_f=/tFBvYjp7Ol3FoboBbWEXoIbUVvWx9yXzrb/l5PL9qL8DRKncEmbOVYXjWJ0VFf8225jzLdY+hJtgpNqxU0AJ+POIX34wSj42uNO13bRXWXBW0jHZhZ7npvrwjkQ6+2rmMKZu2r5frVGUmO7YUdKZWJxnm+lgc852gGsh7iYCFHcQeDXYQaajjlXW86nrROEbYLEs8HK2wLzoiKD55bgLYpkR/5MqIoHx9y2r9+SLfoSIRc7t0+bb1FC9PQQ4tW0q9RZol/RKWX4GzHnFaC84A1P6ZJZVi93MHEc2M4zw5fds487i/rNKBIg5mlyno/jBKr4Rd8aQetCXSB/6YbZt15Hu/D+zBcSwUM3vrEqSp+QoLWqlVyottihe/5VYsQ05ee/Cn6SbOoeXwuhgJWOMtHS0pCMAwPclkDlvB8Ih4vdvBIpMyJVwQ==;ali_apache_track=;_m_h5_tk=6912a4829811b56e757817b4162a2310_1559211406921;_m_h5_tk_enc=ef44c7d59576faeb86252956fbacb129;aep_common_f=2brejd38ciXT52fvJ5tF4pkwfVa6a3fPfTdLcnULqLgjFLGJSwEtkA==;aep_usuc_f=region=US;b_locale=en_US;iss=y;isfm=y;c_tp=USD;x_alimid=230163491;acs_usuc_t=acs_rt=d0b42ccad307496c853585edb9b91d73;x_csrf=131lm59tsqd1t;xman_t=XYJeY1ypQR9K25HOJsd4BQ1U38EsZL+ekW5a8uGXpFFkTjGFrjckYuFS0PK6JMNsHT9T0OV6X7jatUTFq+c5Kp/oaTifJDDmr3C+OeaqkGgYD+J8YS1bxnrtHdVeLhhHPENBINckW6SvbcDV0e37LGYedo32Fk98dCKD+yIkRQjwDfhXINwDj+5HdgFNCy8VqilJFn8jwUPxm+AQDuGJui9bh6WVc9nvA2ClA9oNs69Bp9mIDufQHhC1mKfeCmOsDWS8JPJNbun+4kP/3a4J3YKiDZELjdckVI4ePx5xO/QZdgL2MzUmF7+zLckqL9NPYMXPnn+X6Q1LPBgzRF/2//pSRYDuru12ZnudDWJ5ZNyBI+69C6nXoXqm0uBpALVXW7uDXzHite1QoXsrSzyWtmi1852wap9qxl6to85lYW59CspuMD1RTKQg0uQ2SIwtJr26sK6PI0z5GKvRm52qs93/ChNPPNgcixTpop2sVV81HA+WbdotcM6b9pVRpW4nap/UwB+KH6rSUaFN58aT7ffzzW11OAMXH8B62SAmRut0XUkUsGaBoeAP5qDMruyCURpiGcaZCAqQwiZcU5Zf5Gfl8IYMdTP0x2Ea01a5XgcZQmFml5SXNi5nl86noqOcJndqAJsXObtY8ktFaQLWK5sJoVlkzRw+zxMkxamZQTMKkNHeRdG3lkAZ905Ud2wl;ali_apache_tracktmp=;_hvn_login=13;xman_us_t=x_lid=cn1520100417suyr;sign=y;x_user=y4jydbHD6SqEjgSdfFY2LyKYgxj+xb+c7u34T7U0/wg=;ctoken=15h0qkkd2y6i2;need_popup=y;l_source=aliexpress;aep_usuc_t=ber_l=A0'