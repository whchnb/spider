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
from photoBank.public import Public

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
        local_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Alibaba'
        files = os.listdir(local_path)
        albums_dict = {}
        for file in files:
            albums_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Alibaba\{}'.format(file)
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

    # 获取网络相册分组信息
    def get_online_album(self):
        print('正在获取网络相册分组信息')
        url = 'https://photobank.alibaba.com/photobank/node/ajax/groups/-1.do'
        params = {
            'ctoken': self.ctoken,
        }
        response = requests.get(url, params=params, headers=self.headers, verify=False)
        datas = json.loads(response.text)['object']
        online_album_detail = {i['name']: i['id'] for i in datas if i['parentId'] is None}
        return online_album_detail

    # 获取网上照片信息
    def get_photo(self, groupid, page=1, maxPage=1, photo_list=[]):
        if page > maxPage:
            return photo_list
        url = 'https://photobank.alibaba.com/photobank/node/ajax/photos.do'
        params = {
            'imageWidth': '350',
            'ctoken': self.ctoken,
            'imageHeight': '350',
            'search[groupId]': groupid,  # 308528282
            'page_size': '100',
            'current_page': page,
            'action': 'default',
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = json.loads(response.text)
        total = datas[0]['totalResultsNum']
        photo_datas = datas[1]
        for photo_data in photo_datas:
            photo_detail = {}
            createTime = photo_data['gmtCreate'].replace('T', ' ').split('.')[0]
            timestamp = time.mktime(time.strptime(createTime, "%Y-%m-%d %H:%M:%S"))
            photo_detail['createTime'] = str(timestamp).replace('.', '') + '00'
            photo_detail['filename'] = photo_data['filename']
            photo_detail['displayName'] = photo_data['displayName']
            photo_detail['imageUrl'] = photo_data['imageUrl']
            photo_detail['referenceCount'] = photo_data['referenceCount']
            photo_detail['id'] = photo_data['id']
            photo_list.append(photo_detail)
        if total <= 100:
            return photo_list
        else:
            page += 1
            if total % 100 != 0:
                maxPage = total // 100 + 1
            else:
                maxPage = total // 100
            return self.get_photo(groupid, page=page, maxPage=maxPage, photo_list=photo_list)
        # print(response.text)

    # 更新网络图片
    def update(self, local_album_detail, online_album_detail):
        for local_sku, photo_list in local_album_detail.items():
            local_photo_dict = {i['name']: i['date'] for i in photo_list}
            online_photo_dict = {i['displayName']: i['createTime'] for i in online_album_detail[local_sku][1]}
            album_id = online_album_detail[local_sku][0]
            for name, createTime in local_photo_dict.items():
                if name[:-4] not in online_photo_dict.keys():
                    print('{}不存在，正在上传'.format(name))
                    self.get_update_photo_data(local_sku, name, album_id)
                elif int(createTime) > int(online_photo_dict[name[:-4]]):
                    print('{}正在更新'.format(name))
                    self.get_update_photo_data(local_sku, name, album_id)

    # 获取上传图片数据
    def get_update_photo_data(self, sku, new_photo, album_id):
        print('正在获取上传图片数据')
        set_up_url = 'https://kfupload.alibaba.com/mupload'
        new_photo_path = r'\\192.168.1.98\公共共享盘\@ 电商文档\# 群发素材\Alibaba\{}\{}'.format(sku, new_photo)
        file_name = new_photo
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
        upload_url = 'https://photobank.alibaba.com/photobank/node/ajax/photos/uploadImage.do?ctoken={}'.format(self.ctoken)
        data = {
            "imgListData": [
                {"filename": fileSavePath,
                 "groupId": album_id,
                 "fileMd5": fileMd5,
                 "displayName": fileName,
                 "photobankImageMetadata": {
                     "size": fileSize,
                     "width": fileWidth,
                     "height": fileHeight,
                     "hashCode": fileMd5
                 },
                "photoUrl": '//sc02.alicdn.com/kf/{}'.format(fileSavePath)
                 }
            ],
                "useWatermark": False,
                "photobankImageWatermark": {"frame": "N", "position": "center", "watermarkContent": ""},
                "groupId": album_id}
        print(data)
        headers = self.headers
        headers['content-type'] = 'application/json'
        response = requests.post(url=upload_url, data=json.dumps(data), headers=headers, verify=False)
        print(response.text)

    # 创建分组
    def create_new_album_group(self, difference_groups):
        for sku in difference_groups:
            print('正在创建{}分组'.format(sku))
            url = 'https://photobank.alibaba.com/photobank/node/ajax/groups/.do?ctoken={}'.format(self.ctoken)
            data = {
                'name': sku,
                'parentId': -1
            }
            headers = self.headers
            headers['content-type'] = 'application/json'
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
            print(response)
            print(response.text)
            data = json.loads(response.text)
            status = data['success']
            if status is True:
                print('相册分组{} 创建成功'.format(sku))
            else:
                print(data['errorMessage'])

    def log(self, datas):
        url = 'http://cs1.jakcom.it/Alibaba_storemanage/Albuminfo_save'
        for sku, data in datas.items():
            album_name = sku
            album_ID = data[0]
            Account = self.account
            for photo in data[1]:
                image_name = photo['displayName']
                image_ID = photo['id']
                whether_reference = photo['referenceCount']
                img_url = photo['imageUrl']
                date = str(photo['createTime'])[:10] + '.' + str(photo['createTime'])[10:]
                filename = photo['filename']
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
        online_album_group = self.get_online_album()
        difference_groups = list(set(local_album_detail.keys()).difference(online_album_group.keys()))
        if len(difference_groups) != 0:
            self.create_new_album_group(difference_groups)
        online_album_detail = {}
        online_album_group = self.get_online_album()
        for sku, id in online_album_group.items():
            online_photo_detail = self.get_photo(id, photo_list=[])
            online_album_detail[sku] = [id, online_photo_detail]
        self.update(local_album_detail, online_album_detail)
        self.log(online_album_detail)


def main():
    account_list = [
        'fb1@jakcom.com',
        # 'fb2@jakcom.com',
        # 'fb3@jakcom.com',
        # 'tx@jakcom.com',
    ]
    for account in account_list:
        album = Album(account)
        album.main()


if __name__ == '__main__':
    main()
