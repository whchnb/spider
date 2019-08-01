# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: alibabaFan_with_selenium.py --> fanPass.py
@time: 2019/5/10 17:23
@desc: 自动化完成每日文章发布
@upload time: 2019/5/16
@update detail: 更新了卖点信息，优化了点击添加按钮后资源未加载的问题
@upload time: 2019/06/21
@update detail: 更改selenium任务为API接口任务
"""
import json
import random
import datetime
import requests
from alibaba.public import Public
from DynamicAnnouncement.timeTransfer import timeTransfer


class FanPass(Public):
    def __init__(self, account):
        self.count = 0
        self.account = account
        super(FanPass, self).__init__(self.account)
        self.ctoken = self.get_ctoken()
        self.csrf_token = self.get_csrf_token()

    # 获取文章分类
    def get_t(self):
        tList = [
            {'新品发布': '373016:355030'},
            {'询盘热品': '373016:369002'},
            {'交易热品': '373016:373001'},
            {'性能评测': '373016:373002'},
            {'产品清单': '373016:369003'},
            {'产品展示': '373016:373003'},
            {'促销打折': '373016:373005'},
            {'实地勘厂': '373016:373006'},
            {'生产工艺': '373016:373007'},
            {'公司介绍': '373016:373008'},
            {'仓储运输': '373016:373010'},
            {'定制能力': '373016:350030'},
            {'展会现场': '373016:373015'},
            {'买家评价': '373016:373013'},
        ]
        return tList

    # 添加视频
    def add_video(self, sku):
        print('开始添加视频')
        url = 'https://hz-productposting.alibaba.com/product/ajax_video.do?ctoken=%s' % self.ctoken
        postData = {
            'event': 'fetchList',
            'status': 'all',
            'gmtCreate': None,
            'linkedCount': None,
            'page': 1,
            'pageSize': 10,
            'canUpgrade': None,
            'subject': '%s主图' % sku,
            'quality': None,
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers[
            'referer'] = 'https://hz-productposting.alibaba.com/product/videobank/home.htm?type=video&showDialog=uploadVideo'
        response = requests.post(url, data=postData, headers=headers)
        datas = response.json()['data']['videos']
        if len(datas) != 0:
            data = random.choice(datas)
            return data
        else:
            return None

    def get_img_group(self):
        url = 'https://photobank.alibaba.com/photobank/node/ajax/groups/-1.do'
        params = {
            'ctoken': self.ctoken
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = response.json()['object']
        img_group_dict = {i['name']:i['id'] for i in datas}
        return img_group_dict['活动主图']

    # 添加图片
    def add_img(self, sku):
        print('开始添加图片')
        url = 'https://photobank.alibaba.com/photobank/node/ajax/photos.do'
        group_id = self.get_img_group()

        params = {
            'ctoken': self.ctoken,
            # 'dmtrack_pageid': '3d86fad60b01fdc75d0ca76d16b796e0872b8a25f1',
            'search[displayName]': sku,
            'search[groupId]': group_id,
            'search[lifeStatus]': '1',
            'action': 'default',
            'current_page': '1',
            'page_size': '28',
            'imageWidth': '350',
            'imageHeight': '350',
            # '_': '1561110596720',
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = response.json()[1]
        if len(datas) != 0:
            data = random.choice(datas)
            return data
        else:
            return None

    # 获取商品分类
    def get_group(self):
        url = 'https://hz-productposting.alibaba.com/product/group_ajax.do'
        params = {
            'event': 'listGroupCombine',
            'ctoken': self.ctoken,
            '_csrf_token_': self.csrf_token,
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = {i['name'].lower():i['id'] for i in response.json()['data']}
        return datas

    # 添加商品
    def add_product(self, addProductSku):
        productDatas = []
        for i in range(len(addProductSku)):
            if len(productDatas) >= 9:
                return productDatas
            sku = addProductSku.pop(random.choice(range(len(addProductSku))))
            print('正在添加产品', sku)
            groupData = self.get_group()
            url = 'https://hz-productposting.alibaba.com/product/managementproducts/asyQueryProductsList.do'
            params = {
                'statisticsType': 'month',
                'repositoryType': 'all',
                'imageType': 'all',
                'groupId': groupData['hot sale'],
                'redModel': sku,
                'groupLevel': '1',
                'showType': 'onlyMarket',
                'status': 'all',
                'page': '1',
                'size': '10',
                'ctoken': self.ctoken,
                '_csrf_token_': self.csrf_token,
            }
            response = requests.get(url, params=params, headers=self.headers)
            datas= response.json()['products']
            if len(datas) == 0:
                continue
            productData = random.choice(datas)
            # print(productData)
            # import sys
            # sys.exit()
            addProductData = {
                "bizCode": "icbu",
                "checked": False,
                "coverUrl": 'https://' + productData['absImageUrl'], # "https://sc02.alicdn.com/kf/HTB1O.cSdf1G3KVjSZFkq6yK4XXaH.jpg",
                "finalPricePc": 0,
                "finalPriceWap": 0,
                "images": [],
                "itemId": productData['id'],
                "materialId": str(productData['id']),
                "price": 0,
                "rawTitle": productData['subject'], # "JAKCOM TWS Smart Wireless Headphone new Earphones Headphones like siliconcase antenna man oukitel k10",
                "resourceUrl": "",
                "title":  productData['subject'], # "JAKCOM TWS Smart Wireless Headphone new Earphones Headphones like siliconcase antenna man oukitel k10"
            }
            productDatas.append(addProductData)
        return productDatas

    # 获取formData
    def get_formData(self):
        print("正在获取表单")
        url = "https://cpub.alibaba.com/render.json?from=feed&template=icbuVideo"
        response = requests.get(url, headers=self.headers)
        formData = json.loads(response.text)
        # print(formData)
        data = formData['config']['formData']['serverData']
        # print(a)
        return data

    # 获取actions
    def get_actions(self):
        actions = [
            {
                "size": "large",
                "span": "2",
                "style": {
                    "display": "none"
                },
                "name": "draft",
                "text": "保存草稿",
                "url": "//cpub.alibaba.com/submit.json?draft=1&_draft_id=1&_tb_token_=" + self.tb_token
            },
            {
                "size": "large",
                "span": 2,
                "offset": 5,
                "type": "primary",
                "needValidate": True,
                "disabled": False,
                "style": {
                    "display": "none"
                },
                "name": "submit",
                "text": "发布(今日还可发布：4篇)",
                "url": "//cpub.alibaba.com/submit.json?_tb_token_=" + self.tb_token
            },
            {
                "size": "large",
                "span": "2",
                "style": {
                    "display": "none"
                },
                "name": "preview",
                "text": "预览",
                "url": "//cpub.alibaba.com/submit.json?preview=1&draft=1&_draft_id=1&_tb_token_=" + self.tb_token
            }
        ]
        return actions

    # 获取children
    def get_children(self, sku, tData, videoData, imgData, productData):
        # print(productData)
        t = list(tData.keys())[0]
        v = list(tData.values())[0]
        self.videoId = videoData['videoId']
        self.videoName = videoData['videoName']
        date = str(datetime.datetime.now().date()).replace('-', '')
        title = '%s-%s-%s' % (sku, t, date)
        self.feedType = t
        self.title = title
        self.sku = sku
        sellPoint = 'Products, accessories, packaging,  All-round free customization;\nArrange shipping within 24 hours;\nNo increase in price.\nNo MOQ limit..'
        children = [
            # 标题
            {
                "component": "Input",
                "label": "",
                "name": "title",
                "props": {
                    "label": "",
                    "placeholder": "不作为内容标题，而是用于后续管理识别",
                    "cutString": False,
                    "maxLength": 64,
                    "hasLimitHint": True,
                    "value": title
                },
                "rules": [
                    {
                        "type": "string",
                        "message": "标题不能为空",
                        "required": True
                    },
                    {
                        "min": 4,
                        "type": "string",
                        "message": "文字长度太短, 要求长度最少为4"
                    },
                    {
                        "max": 64,
                        "type": "string",
                        "message": "文字长度太长, 要求长度最多为64"
                    }
                ]
            },
            # 卖点
            {
                "component": "Input",
                "label": "",
                "name": "summary",
                "props": {
                    "multiple": True,
                    "label": "",
                    "placeholder": "请用英文简要描述推送商品的卖点、亮点，140字以内",
                    "rows": 4,
                    "cutString": False,
                    "maxLength": 140,
                    "hasLimitHint": True,
                    "value": sellPoint
                },
                "rules": [
                    {
                        "type": "string",
                        "message": "不能为空",
                        "required": True
                    },
                    {
                        "min": 10,
                        "type": "string",
                        "message": "文字长度太短, 要求长度最少为10"
                    },
                    {
                        "max": 140,
                        "type": "string",
                        "message": "文字长度太长, 要求长度最多为140"
                    }
                ]
            },
            # 视频
            {
                "component": "IceAddVideo",
                "label": "上传视频",
                "name": "body",
                "props": {
                    "editVideoUrl": "https://hz-productposting.alibaba.com/product/videobank/home.htm",
                    "addImageProps": {
                        "pixFilter": "",
                        "uploadApi": "https://message.alibaba.com/message/content/material/uploadPic.htm",
                        "categoryListApi": "https://message.alibaba.com/message/content/material/photoBankGroup.htm",
                        "appkey": "tu",
                        "disableStatusCheck": True
                    },
                    "label": "上传视频",
                    "api": "https://message.alibaba.com/message/content/material/pageVideo.htm",
                    "videoCenterUrl": "https://hz-productposting.alibaba.com/product/videobank/home.htm",
                    "isNewAPI": True,
                    "tips": "推荐上传16：9或者9：16的视频，在5秒～30秒之内",
                    "enableNormalVideo": True,
                    "value": [
                        {
                            "coverUrl":  videoData['coverUrl'], # "https://img.alicdn.com/imgextra/i3/6000000003623/O1CN01JvlC9V1cdNTzIIhb2_!!6000000003623-0-tbvideo.jpg"
                            "duration": videoData['duration'], # 30
                            "playUrl": "//cloud.video.taobao.com/play/u/2153292369/p/1/e/6/t/10300/%s.mp4" % videoData['videoId'],
                            "title": videoData['videoName'], # "WE2描述页-18.mp4",
                            "uploadTime": timeTransfer(videoData['gmtCreate']),
                            "videoCoverUrl": imgData['imageUrl'], # "//sc01.alicdn.com/kf/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0/222438073/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0.jpg",
                            "videoId": videoData['videoId']
                        }
                    ]
                },
                "rules": [
                    {
                        "min": 1,
                        "type": "array",
                        "message": "至少要有1个"
                    },
                    {
                        "max": 1,
                        "type": "array",
                        "message": "最多允许1个"
                    }
                ],
                "tips": "推荐上传16：9或者9：16的视频，在5秒～30秒之内",
                "updateOnChange": "true"
            },
            # 封面图
            {
                "component": "CreatorAddImage",
                "label": "",
                "name": "standardCoverUrl",
                "props": {
                    "max": 1,
                    "min": 0,
                    "categoryListApi": "https://message.alibaba.com/message/content/material/photoBankGroup.htm",
                    "uploadApi": "https://message.alibaba.com/message/content/material/uploadPic.htm",
                    "label": "",
                    "uploadTips": "上传封面图",
                    "tips": "请上传尺寸不小于343X343的图片，图片会自动裁剪成1：1。用于Feeds列表页与其他推荐场景展示",
                    "disableStatusCheck": True,
                    "value": [
                        {
                            "materialId": 0,
                            "fileId": 0,
                            "fileName": imgData['displayName'],
                            "folderId": "0",
                            "formatSize": "",
                            "pix": "1000x1000",
                            "sizes": 0,
                            "thumbUrl": imgData['imageUrl'] + '_200x200', # "//sc01.alicdn.com/kf/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0/222438073/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0.jpg_200x200",
                            "url": imgData['imageUrl'], # "//sc01.alicdn.com/kf/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0/222438073/HTB1XMFTb2c3T1VjSZPfq6AWHXXa0.jpg"
                        }
                    ]
                },
                "rules": [
                    {
                        "min": 0,
                        "type": "array",
                        "message": "至少要有0个"
                    },
                    {
                        "max": 1,
                        "type": "array",
                        "message": "最多允许1个"
                    }
                ],
                "tips": "请上传尺寸不小于343X343的图片，图片会自动裁剪成1：1。用于Feeds列表页与其他推荐场景展示"
            },
            # 产品
            {
                "component": "CreatorAddItem",
                "label": "添加产品",
                "name": "bodyItems",
                "props": {
                    "disableUpload": True,
                    "max": 9,
                    "addImageProps": {
                        "categoryListApi": "https://message.alibaba.com/message/content/material/photoBankGroup.htm",
                        "uploadApi": "https://message.alibaba.com/message/content/material/uploadPic.htm",
                        "disableStatusCheck": True
                    },
                    "enableAliCDNSuffix": False,
                    "label": "添加产品",
                    "tips": "<span style=\"font-size: 12px; color: #333333; margin: 0 auto; padding: 5px; border-radius: 4px; background-color: #f5f5f5;\"><img src=\"https://gw.alicdn.com/tfs/TB1ryboVQvoK1RjSZFwXXciCFXa-28-22.png\" style=\"width: 14px; height: 13px;\" alt=\"warning\">请选择精品商品,第9个非精选商品</span>",
                    "activityId": 0,
                    "min": 1,
                    "categoryListApi": "https://message.alibaba.com/message/content/material/productGroup.htm",
                    "categoryListApiQuery": {},
                    "triggerTips": "添加产品",
                    "editTitleMaxLength": 33,
                    "currencyUnit": "$",
                    "value": productData
                },
                "rules": [
                    {
                        "min": 1,
                        "type": "array",
                        "message": "至少要有1个"
                    },
                    {
                        "max": 9,
                        "type": "array",
                        "message": "最多允许9个"
                    }
                ],
                "tips": "<span style=\"font-size: 12px; color: #333333; margin: 0 auto; padding: 5px; border-radius: 4px; background-color: #f5f5f5;\"><img src=\"https://gw.alicdn.com/tfs/TB1ryboVQvoK1RjSZFwXXciCFXa-28-22.png\" style=\"width: 14px; height: 13px;\" alt=\"warning\">请选择精品商品,第9个非精选商品</span>",
                "updateOnChange": "true"
            },
            # feed 分类
            {
                "component": "TagPicker",
                "label": "视频分类",
                "name": "classification",
                "props": {
                    "showTabs": True,
                    "label": "视频分类",
                    "dataSource": {
                        "Feed内容类型": [
                            {
                                "parent": "Feed内容类型",
                                "label": "新品发布",
                                "value": "373016:355030",
                                "checked": True if t == '新品发布' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "询盘热品",
                                "value": "373016:369002",
                                "checked": True if t == '询盘热品' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "交易热品",
                                "value": "373016:373001",
                                "checked": True if t == '交易热品' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "性能评测",
                                "value": "373016:373002",
                                "checked": True if t == '性能评测' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "产品清单",
                                "value": "373016:369003",
                                "checked": True if t == '产品清单' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "产品展示",
                                "value": "373016:373003",
                                "checked": True if t == '产品展示' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "促销打折",
                                "value": "373016:373005",
                                "checked": True if t == '促销打折' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "实地勘厂",
                                "value": "373016:373006",
                                "checked": True if t == '实地勘厂' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "生产工艺",
                                "value": "373016:373007",
                                "checked": True if t == '生产工艺' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "公司介绍",
                                "value": "373016:373008",
                                "checked": True if t == '公司介绍' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "仓储运输",
                                "value": "373016:373010",
                                "checked": True if t == '仓储运输' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "定制能力",
                                "value": "373016:350030",
                                "checked": True if t == '定制能力' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "展会现场",
                                "value": "373016:373015",
                                "checked": True if t == '展会现场' else False
                            },
                            {
                                "parent": "Feed内容类型",
                                "label": "买家评价",
                                "value": "373016:373013",
                                "checked": True if t == '买家评价' else False
                            }
                        ]
                    },
                    "value": [v]
                },
                "rules": [
                    {
                        "min": 1,
                        "type": "array",
                        "message": "至少要有1个"
                    },
                    {
                        "max": 1,
                        "type": "array",
                        "message": "最多允许1个"
                    }
                ]
            }
        ]
        return children

    # 发布
    def save(self, formData, actions, children):
        url = 'https://cpub.alibaba.com/submit.json?_tb_token_=%s' % self.tb_token
        data = {
            'config': json.dumps({
                "actions": actions,
                "children": children,
                "dynamicFormVersion": "0.1.16",
                "formData": {
                    "template": "icbuVideo",
                    "owner": "icbu",
                    "formName": "",
                    "activityName": "",
                    "source": "creator",
                    "userRole": "icbuSeller",
                    "publishToolbar": "[{\"text\":\"发布新微淘\"}]",
                    "serverData": formData
                },
                "labelCol": 3,
                "name": "PUBLISH_FORM__PC",
                "updateUrl": "//cpub.alibaba.com/async.json?_tb_token_=%s" % self.tb_token
            })
        }
        print(json.dumps({
                "actions": actions,
                "children": children,
                "dynamicFormVersion": "0.1.16",
                "formData": {
                    "template": "icbuVideo",
                    "owner": "icbu",
                    "formName": "",
                    "activityName": "",
                    "source": "creator",
                    "userRole": "icbuSeller",
                    "publishToolbar": "[{\"text\":\"发布新微淘\"}]",
                    "serverData": formData
                },
                "labelCol": 3,
                "name": "PUBLISH_FORM__PC",
                "updateUrl": "//cpub.alibaba.com/async.json?_tb_token_=%s" % self.tb_token
            }, ensure_ascii=False))
        self.headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers[
            'referer'] = 'https://creator.alibaba.com/publish/post?spm=a2700.11704259.0.0.3c1465aaBlPU2O&from=draft&template=icbuVideo'
        self.headers['origin'] = 'https://creator.alibaba.com'
        response = requests.post(url, headers=self.headers, data=data)
        status = response.json()['status']
        print(response.json())
        if len(response.text) > 200:
            print('*-*-' * 50)
            print(response.text)
            print('*-*-' * 50)
            data = response.json()['config']
            data['children'][6].pop('errMsg')
            data['children'][6]['props']['value']['hasRead'] = True
            data['children'][6]['props']['value']['hidden'] = True
            data = {
                'config': json.dumps(data)
            }
            response = requests.post(url, headers=self.headers, data=data)
            print('*-*-' * 50)
            print(response.text)
            print('*-*-' * 50)
        self.count += 1
        self.send_fanPass_log()

    # 获取sku
    def get_sku(self):
        url = "http://192.168.1.160:90/alibaba/Get_tempurl_byaccount"
        response = requests.get(url).text
        sku_datas = json.loads(response)
        sku_dict = {}
        for sku_data in sku_datas:
            if sku_data["SKU"] in sku_dict.keys():
                sku_dict[sku_data["SKU"]].append(sku_data["Temp_Links"])
            else:
                sku_dict[sku_data["SKU"]] = [sku_data["Temp_Links"]]
        sku_list = list(sku_dict.keys())
        if "BH2" in sku_list:
            sku_list.remove("BH2")
        if "H1" in sku_list:
            sku_list.remove("H1")
        return sku_list

    # 粉丝通日志
    def send_fanPass_log(self):
        fanPass_log_url = 'http://192.168.1.160:90/alibaba/Log_feed_promotion'
        data = {
            'Account': self.account,
            'FeedVideo': self.videoName,
            'VideoID': self.videoId,
            'FeedType': self.feedType,
            'FeedTitle': self.title,
            'SKU': self.sku,
            'Createtime': str(datetime.datetime.now())
        }
        fanPass_log_response = requests.post(url=fanPass_log_url, data=data)
        print('fanPass_log_response', fanPass_log_response)

    def main(self):
        sku_list = self.get_sku()
        tList = self.get_t()
        for sku in sku_list:
            print(sku)
            if self.count == 8:
                print('今天发布文章', self.count)
                return
            addProductSku = self.get_sku()
            addProductSku.remove(sku)
            tData = tList.pop(random.choice(range(len(tList))))
            videoData = self.add_video(sku)
            imgData = self.add_img(sku)
            productData = self.add_product(addProductSku)
            if videoData is None or imgData is None:
                tList.append(tData)
                continue
            formData = self.get_formData()
            actions = self.get_actions()
            children = self.get_children(sku, tData, videoData, imgData, productData)
            try:
                self.save(formData, actions, children)
            except Exception as e:
                print(e)
                continue


def main():
    account_list = [
        # 'fb1@jakcom.com',
        # 'fb2@jakcom.com',
        # 'fb3@jakcom.com',
        'tx@jakcom.com',
    ]
    for account in account_list:
        print(account)
        fanPass = FanPass(account)
        fanPass.main()


if __name__ == '__main__':
    main()
