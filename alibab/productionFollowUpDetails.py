# encoding:utf-8
"""
@author:Liwenhao
@e-mail:wh.chnb@gmail.com
@file:productionFollowUpDetails.py
@time:2019/6/5 19:29
@desc:
@fwd : 修改urllib3 下fileds.py 源码(45,46)
"""
import os
import sys
import time
import json
import urllib3
import requests
from alibaba.public import Public
from urllib.parse import urlencode
# urllib3.contrib.pyopenssl.extract_from_urllib3()
# requests.packages.urllib3.disable_warnings()
# ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings()


class ProductionFollowUpDetails(Public):
    def __init__(self, account, order_id, sku, express_info):
        self.account = account
        self.sku = sku
        self.order_id = order_id
        self.express_info = express_info
        super(ProductionFollowUpDetails, self).__init__(self.account)
        self.ctoken = self.get_ctoken()
        self.code_status_dict = self.get_column_code()

    # 获取本地图片信息
    def get_local_img(self, sku):
        local_path = r'\\192.168.1.98\公共共享盘\1_产品文档\实物\{}'.format(sku)
        img_files = os.listdir(local_path)
        img_files_dict = {
            # 正面图
            'picturesOfSampleProductsFront': [],
            # 背面图
            'picturesOfSampleProductsBack': [],
            # 侧面图
            'picturesOfSampleProductsSide': [],
            # 视频
            'videoOfSampleProducts': [],
            # 细节图
            'picturesOfProductsDetails': [],
            # 远景图
            'picturesOfAllLabeledProductsLongShot': [],
            # 包装后成品图
            'picturesOfPackingFinishedProduct':[],
            # 批量成品堆放图
            'picturesOfFinishedProducts': [],
            # 产品装箱未封箱图
            'picturesOfPackedProducts': [],
            # 产品装箱封箱图
            'picturesOfLabeledBoxesOrPallets': [],
            # 产品外箱图贴仓库标签或托盘图
            'pictureOfProdcutsInPalletWithShippingLabels': [],
        }
        for img_file in img_files:
            img_path = local_path + r'\%s' % img_file
            img_size = os.path.getsize(img_path)
            img_data = (img_file, img_size, img_path)
            if '正面' in img_file:
                img_files_dict['picturesOfSampleProductsFront'].append(img_data)
            elif '背面' in img_file:
                img_files_dict['picturesOfSampleProductsBack'].append(img_data)
            elif '侧面' in img_file:
                img_files_dict['picturesOfSampleProductsSide'].append(img_data)
            elif '视频' in img_file:
                img_files_dict['videoOfSampleProducts'].append(img_data)
            elif '包装图1' in img_file or '组合图' in img_file or '配件图' in img_file:
                img_files_dict['picturesOfProductsDetails'].append(img_data)
            elif '包装底部' in img_file:
                img_files_dict['picturesOfAllLabeledProductsLongShot'].append(img_data)
            elif '包装图2' in img_file:
                img_files_dict['picturesOfPackingFinishedProduct'].append(img_data)
            elif '堆货图1' in img_file:
                img_files_dict['picturesOfFinishedProducts'].append(img_data)
            elif '一号箱空箱照' in img_file:
                img_files_dict['picturesOfPackedProducts'].append(img_data)
            elif '一号箱满箱照' in img_file:
                img_files_dict['picturesOfLabeledBoxesOrPallets'].append(img_data)
            elif '一号箱封箱照' in img_file:
                img_files_dict['pictureOfProdcutsInPalletWithShippingLabels'].append(img_data)
        return img_files_dict

    # 检测图片
    def check_file(self, mainCrmFileId):
        url = 'https://crm-file.alibaba-inc.com/crmfile/token/checkFile.json'
        data = {
            'chunks': 1,
            'mainCrmFileId': mainCrmFileId
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(self.order_id)
        headers['Origin'] = 'onetouch.alibaba.com'
        response = requests.post(url, headers=headers, data=data, verify=False)

    # 上传图片
    def upload_img(self, img_data, chunk=0, chunkIndex=0, chunks=1, size=None, full_size=None, img_ali_name=None, t='image/jpeg'):
        # 上传视频需要的参数为chunk chunkIndex chunks size full_size img_ali_name
        # 若传入img_ali_name 则表明上传视频
        img_ali_name = self.get_ali_name(img_data) if img_ali_name is None else img_ali_name
        img_name = img_data[0]
        img_size = img_data[1] if size is None else size
        full_size = img_data[1] if full_size is None else full_size
        img_path = img_data[2]
        url = 'https://crm-file.alibaba-inc.com/crmfile/token/doUpload.json'
        boundry = '------WebKitFormBoundaryJz3PjcmgHvVYpfcc'
        fireFox_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Host": "crm-file.alibaba-inc.com",
            "Origin": "https://onetouch.alibaba.com",
            # "Content-Type":"multipart/form-data; boundary={}".format(boundry),
            "Pragma": "no-cache",
            "Referer": "https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}".format(self.order_id),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        }
        fr = open(img_path, 'rb').read()
        data = {
            'id': 5400369145282851,
            'chunk': chunk,
            'chunkIndex': chunkIndex,
            'chunks': chunks,
            'loadsize': str(img_size),
            'big': True,
            'size': str(full_size),
            'type': t,
            'ownerApp': 'crmfile',
            'sceneCode': 'default_chunk',
            'mainCrmFileId': img_ali_name,
        }
        fields = {
            'file': (img_name, fr, 'application/octet-stream')
        }
        response = requests.post(url, headers=fireFox_headers, files=fields, data=data, verify=False)
        # 若上传视频，直接返回img_ali_name
        if t != 'image/jpeg':
            return img_ali_name
        status = json.loads(response.text)['hasError']
        # status 为 false 表明上传成功
        if status is False:
            # self.check_file(img_ali_name)
            return img_ali_name
        else:
            print(response.text)

    # 添加正面图片
    def add_front_img(self, img_datas):
        subtemp_2_group_1_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfSampleProductsFront01'
            else:
                name = 'picturesOfSampleProductsFrontOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        if len(img_datas) < 4:
            front_dict = {
                'picturesOfSampleProductsBackOption04': {
                    "value": "",
                    "title": "样品确认图（正面）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        return subtemp_2_group_1_1_mediaset

    # 添加背面图片
    def add_back_img(self, img_datas):
        subtemp_2_2_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfSampleProductsBack01'
            else:
                name = 'picturesOfSampleProductsBackOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        if len(img_datas) < 4:
            front_dict = {
                'picturesOfSampleProductsBackOption04': {
                    "value": "",
                    "title": "样品确认图（背面）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        return subtemp_2_2_group_1_mediaset

    # 添加侧面图片
    def add_side_img(self, img_datas):
        subtemp_2_3_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfSampleProductsSide01'
            else:
                name = 'picturesOfSampleProductsSideOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_3_group_1_mediaset.append(front_dict)
        if len(img_datas) < 4:
            front_dict = {
                'picturesOfSampleProductsSideOption04': {
                    "value": "",
                    "title": "样品确认图（侧面）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_3_group_1_mediaset.append(front_dict)
        return subtemp_2_3_group_1_mediaset

    # 添加视频
    def get_video(self, img_datas):
        subtemp_2_4_group_1_mediaset = []
        # 若视频大于5M 需分开上传
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_size = img_data[1]
            chunks = int(img_size) // 5120000 if int(img_size) % 5120000 == 0 else int(img_size) // 5120000 + 1
            img_ali_name = self.get_ali_name(img_data, t='mp4')
            for chunk in range(chunks):
                size = 5120000
                if chunk == chunks - 1:
                    size = img_size - chunk * 5120000
                img_ali_name = self.upload_img(img_data, chunk=chunk, chunkIndex=chunk, chunks=chunks, size=size, full_size =img_size, img_ali_name=img_ali_name, t='video/mp4')
            if index == 0:
                name = 'videoOfSampleProducts01'
            else:
                name = 'videoOfSampleProductsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)
        for i in range(2,4):
            front_dict = {
                'videoOfSampleProductsOption0{}'.format(i): {
                    "value": "",
                    "title": "样品确认图（侧面）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)
        return subtemp_2_4_group_1_mediaset

    # 添加资源包分享
    def add_resource_pack(self):
        resource_path = r'\\192.168.1.98\公共共享盘\1_产品文档\营销资料\下载说明'
        img_files = os.listdir(resource_path)
        img_list = []
        for img_file in img_files:
            img_path = resource_path + '/' + img_file
            img_size = os.path.getsize(img_path)
            img_list.append((img_file, img_size, img_path))
        subtemp_2_group_1_2_mediaset = []
        for index, img_data in enumerate(img_list):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'exclusiveProductPicturesOrVideos01'
            else:
                name = 'exclusiveProductPicturesOrVideosOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_group_1_2_mediaset.append(front_dict)
        if len(img_list) < 3:
            front_dict = {
                'picturesOfSampleProductsSideOption03': {
                    "value": "",
                    "title": "资源包分享图",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_group_1_2_mediaset.append(front_dict)
        return subtemp_2_group_1_2_mediaset

    # 添加产品细节图
    def add_detail_img(self, img_datas):
        subtemp_2_group_1_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfProductsDetails01'
            else:
                name = 'picturesOfProductsDetailsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        if len(img_datas) < 4:
            front_dict = {
                'picturesOfProductsDetailsOption04': {
                    "value": "",
                    "title": "产成品细节图（近景）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        return subtemp_2_group_1_1_mediaset

    # 添加出产检测报告
    def add_product_report(self):
        reports_path = r'\\192.168.1.98\公共共享盘\@ 公司内务文档\资质手续\质检认证\证书文档\{}\CE'.format(self.sku)
        report_files = os.listdir(reports_path)
        report_name = [report_file for report_file in report_files if 'jpg' in report_file][0]
        report_path = reports_path + '/' + report_name
        report_size = os.path.getsize(report_path)
        report_datas = [(report_name, report_size, report_path)]
        subtemp_2_4_group_1_mediaset = []
        for index, img_data in enumerate(report_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)

            front_dict = {
                'picturesOfProductsTestReport01': {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)
        for i in range(2, 5):
            name = 'picturesOfProductsTestReportOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "出厂检测报告",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)

        return subtemp_2_4_group_1_mediaset

    # 单位贴标图(近景)
    def add_close_shot(self):
        close_host_path = r'\\192.168.1.98\公共共享盘\@ 公司内务文档\资质手续\质检认证\证书文档\{}\EAN'.format(self.sku)
        close_host_files = os.listdir(close_host_path)
        img_datas = []
        for close_host_file in close_host_files:
            if 'jpg' in close_host_file:
                img_name = close_host_file
                img_path = close_host_path + '/' + img_name
                img_size = os.path.getsize(img_path)
                img_datas.append((img_name, img_size, img_path))
        picturesOfLabeledProductsCloseShot = []
        for index, img_data in enumerate(img_datas):
            if index == 0:
                name = 'picturesOfLabeledProductsCloseShot01'
            else:
                name =  'picturesOfLabeledProductsCloseShotOption0{}'.format(index + 1)
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            picturesOfLabeledProductsCloseShot.append(front_dict)
        if len(img_datas) > 3:
            return picturesOfLabeledProductsCloseShot
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfLabeledProductsCloseShotOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "最小销售单位贴标图(近景)",
                    "from": "all",
                    "url": ""
                }
            }
            picturesOfLabeledProductsCloseShot.append(front_dict)
        return picturesOfLabeledProductsCloseShot

    # 销售单位贴标图(远景)
    def add_vision(self, img_datas):
        subtemp_2_2_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            if index == 0:
                name = 'picturesOfAllLabeledProductsLongShot01'
            else:
                name = 'picturesOfAllLabeledProductsLongShotOption0{}'.format(index + 1)
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_2_group_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfAllLabeledProductsLongShotOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "最小销售单位贴标图(远景)",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        return subtemp_2_2_group_1_mediaset

    # 包装后成品图（近景）
    def add_packaged_product_img(self, img_datas):
        subtemp_2_group_1_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfPackingFinishedProduct01'
            else:
                name = 'picturesOfPackingFinishedProductOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_group_1_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfAllLabeledProductsLongShotOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "包装后成品图（近景）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_group_1_1_mediaset.append(front_dict)
        return subtemp_2_group_1_1_mediaset

    # 成品堆放图（远景）
    def add_product_stacking_img(self, img_datas):
        subtemp_2_2_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfFinishedProducts01'
            else:
                name = 'picturesOfFinishedProductsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_2_group_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfFinishedProductsOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "批量成品堆放图（远景）",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_2_group_1_mediaset.append(front_dict)
        return subtemp_2_2_group_1_mediaset

    # 装箱未封箱图
    def add_unsealed_img(self, img_datas):
        subtemp_2_3_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfPackedProducts01'
            else:
                name = 'picturesOfPackedProductsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_3_group_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_3_group_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfPackedProductsOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "产品装箱未封箱图",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_3_group_1_mediaset.append(front_dict)
        return subtemp_2_3_group_1_mediaset

    # 产品装箱封箱图
    def add_sealed_img(self, img_datas):
        subtemp_2_4_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'picturesOfLabeledBoxesOrPallets01'
            else:
                name = 'picturesOfLabeledBoxesOrPalletsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_4_group_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'picturesOfLabeledBoxesOrPalletsOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "产品装箱封箱图",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_4_group_1_mediaset.append(front_dict)
        return subtemp_2_4_group_1_mediaset

    # 产品外箱图贴仓库标签或托盘图
    def add_warehouse_label_img(self, img_datas):
        subtemp_2_5_group_1_mediaset = []
        for index, img_data in enumerate(img_datas):
            img_name = img_data[0]
            img_ali_name = self.upload_img(img_data)
            if index == 0:
                name = 'pictureOfProdcutsInPalletWithShippingLabels01'
            else:
                name = 'pictureOfProdcutsInPalletWithShippingLabelsOption0{}'.format(index + 1)
            front_dict = {
                name: {
                    "value": img_ali_name,
                    "title": img_name,
                    "from": "all",
                    "url": img_ali_name
                }
            }
            subtemp_2_5_group_1_mediaset.append(front_dict)
        if len(img_datas) > 3:
            return subtemp_2_5_group_1_mediaset
        for i in range(len(img_datas) + 1, 5):
            name = 'pictureOfProdcutsInPalletWithShippingLabelsOption0{}'.format(i)
            front_dict = {
                name: {
                    "value": "",
                    "title": "产品外箱图贴仓库标签或托盘图",
                    "from": "all",
                    "url": ""
                }
            }
            subtemp_2_5_group_1_mediaset.append(front_dict)
        return subtemp_2_5_group_1_mediaset

    # 获取图片阿里名称
    def get_ali_name(self, img_data, t=None):
        url = 'https://crm-file.alibaba-inc.com/crmfile/token/createWygMainFile.json'
        img_name = img_data[0]
        img_size = img_data[1]
        if t is None:
            data = {
                'addFileParam': '{"fileType":"online","fileName":"%s","fileSize":%d,"categoryId":1501,"templateId":"1701","fileExts":null}' % (
                    img_name, img_size),
                'context': '{"tenantId":"301","operator":"223324529","originSystem":"onetouch-proofcenter"}'
            }
        else:
            data = {
                'addFileParam': json.dumps({"fileType":"online","fileName":img_name,"fileSize":img_size,"categoryId":1501,"templateId":"1701","fileExts":None,"contentType":"video/mp4"}),
                'context': json.dumps({"tenantId":"301","operator":"223324529","originSystem":"onetouch-proofcenter"})
            }
        print(data)
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['accept'] = 'application/json, text/plain, */*'
        headers['origin'] = 'https://onetouch.alibaba.com'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(
            self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        img_name = json.loads(response.text)['content']['result']
        return img_name

    # 获取标签id
    def get_column_code(self):
        url = 'https://onetouch.alibaba.com/moSurvey/seller/detail.json'
        params = {
            'tradeOrderId': self.order_id,
            '_tb_token_': self.tb_token,
            'ctoken':self.ctoken
        }
        headers = self.headers
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(self.order_id)
        headers['authority'] = 'onetouch.alibaba.com'
        headers.pop('origin')
        headers.pop('content-type')
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        response_datas = json.loads(response.text)['data']['taScheduleTaskItemDTOList']
        code_status_dict = {}
        for index, data in enumerate(response_datas):
            taskId = data['authTemplateDTO']['taskId']
            version = data['authTemplateDTO']['splitTaskTemplateData']['version']
            taskSnapshotId = data['authTemplateDTO']['splitTaskTemplateData']['taskSnapshotId']
            if index == 0:
                code_status_dict['save_sample_photo'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
            elif index == 1:
                code_status_dict['save_resource_pack'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
            elif index == 2:
                code_status_dict['save_detail_img'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
            elif index == 3:
                code_status_dict['internal_standard'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
            elif index == 4:
                code_status_dict['external_standard'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
            elif index == 5:
                code_status_dict['get_information'] = {
                    'taskId': taskId,
                    'taskSnapshotId': taskSnapshotId,
                    'version': version
                }
        return code_status_dict

    # 获取备注
    def get_remarks(self, t):
        url = 'http://py1.jakcom.it:5000/get/info/sku_detail/{}'.format(self.sku)
        response = requests.get(url)
        data = eval(response.text)
        if t != 'Barcode':
            remakr_dict = {i.split(':')[0]:i.split(':')[1].strip() for i in data['Description'].split('\n')[1:]}
            return remakr_dict[t]
        else:
            return data[t]

    # 样品照片上传
    def save_sample_photo(self, url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset):
        subtemp_2_5_group_1_textarea = self.get_remarks('Inner White Box')
        taskId = self.code_status_dict['save_sample_photo']['taskId']
        version = self.code_status_dict['save_sample_photo']['version']
        taskSnapshotId = self.code_status_dict['save_sample_photo']['taskSnapshotId']
        # 保存草稿
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(
        #     self.tb_token, self.ctoken)
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        templateStr = {
            "subtemp_2_group_1_1_mediaset":subtemp_2_group_1_1_mediaset,
            "subtemp_2_2_group_1_mediaset":subtemp_2_2_group_1_mediaset,
            "subtemp_2_3_group_1_mediaset":subtemp_2_3_group_1_mediaset,
            "subtemp_2_4_group_1_mediaset":subtemp_2_4_group_1_mediaset,
            "subtemp_2_5_group_1_textarea":subtemp_2_5_group_1_textarea
        }
        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO":{"taskId":taskId,"version":version},"templateStr":json.dumps(templateStr),"taskSnapshotId":taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 电商资源包分享
    def save_resource_pack(self, url, subtemp_2_group_1_2_mediaset):
        subtemp_2_2_group_1_textarea = 'Please follow this below link to view and download all the marketing material of your goods;\nhttp://file.jakcom.com'
        taskId = self.code_status_dict['save_resource_pack']['taskId']
        version = self.code_status_dict['save_resource_pack']['version']
        taskSnapshotId = self.code_status_dict['save_resource_pack']['taskSnapshotId']
        # 保存草稿
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(
        #     self.tb_token, self.ctoken)
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        templateStr = {"subtemp_2_group_1_2_mediaset":subtemp_2_group_1_2_mediaset,"subtemp_2_2_group_1_textarea":subtemp_2_2_group_1_textarea}
        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO":{"taskId":taskId,"version":version},"templateStr":json.dumps(templateStr),"taskSnapshotId":taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 检测完成
    def save_detail_img(self, url, subtemp_2_group_1_1_mediaset, subtemp_2_4_group_1_mediaset):
        subtemp_2_2_group_1_textarea = 'Warranty is 1 year.\nhere are any problems within one year, we will fix or change it for you, and we are responsible for the freight when we send to you.'
        taskId = self.code_status_dict['save_detail_img']['taskId']
        version = self.code_status_dict['save_detail_img']['version']
        taskSnapshotId = self.code_status_dict['save_detail_img']['taskSnapshotId']
        # 保存草稿
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(
        #     self.tb_token, self.ctoken)
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        templateStr = {
            "subtemp_2_group_1_1_mediaset":subtemp_2_group_1_1_mediaset,
            "subtemp_2_2_group_1_mediaset": [{"videoOWholeInspectionProgress01": {"value": "", "title": "全检视频", "url": ""}},
                                  {"videoOWholeInspectionProgressOption02": {"value": "", "title": "全检视频", "url": ""}},
                                  {"videoOWholeInspectionProgressOption03": {"value": "", "title": "全检视频", "url": ""}}],
            "subtemp_2_3_group_1_mediaset": [{"videoOfInspection01": {"value": "", "title": "检测过程视频", "url": ""}},
                                  {"videoOfInspectionOption02": {"value": "", "title": "检测过程视频", "url": ""}},
                                  {"videoOfInspectionOption03": {"value": "", "title": "检测过程视频", "url": ""}}],
            "subtemp_2_4_group_1_mediaset": subtemp_2_4_group_1_mediaset,
            "subtemp_2_5_group_1_textarea":subtemp_2_2_group_1_textarea}
        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO":{"taskId":taskId,"version":version},"templateStr":json.dumps(templateStr),"taskSnapshotId":taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 帖内标
    def internal_standard(self, url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset):
        subtemp_2_4_group_1_textarea = self.get_remarks('Barcode')
        taskId = self.code_status_dict['internal_standard']['taskId']
        version = self.code_status_dict['internal_standard']['version']
        taskSnapshotId = self.code_status_dict['internal_standard']['taskSnapshotId']
        # 保存草稿
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(
        #     self.tb_token, self.ctoken)
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        templateStr = {
             "subtemp_2_group_1_1_mediaset": subtemp_2_group_1_1_mediaset,
             "subtemp_2_2_group_1_mediaset": subtemp_2_2_group_1_mediaset,
             "subtemp_2_3_group_1_mediaset": [{"VideoOfAllLabeledProducts01": {"value": "", "title": "产品贴标视频", "url": ""}},
                                              {"VideoOfAllLabeledProductsOption02": {"value": "", "title": "产品贴标视频", "url": ""}},
                                              {"VideoOfAllLabeledProductsOption03": {"value": "", "title": "产品贴标视频", "url": ""}}],
             "subtemp_2_4_group_1_textarea": subtemp_2_4_group_1_textarea}

        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO": {"taskId": taskId, "version": version},
                                "templateStr": json.dumps(templateStr), "taskSnapshotId": taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(
            self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 打包贴外标
    def external_standard(self, url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset, subtemp_2_5_group_1_mediaset):
        subtemp_2_7_group_1_textarea = self.get_remarks('Outer Brown Box')
        taskId = self.code_status_dict['external_standard']['taskId']
        version = self.code_status_dict['external_standard']['version']
        taskSnapshotId = self.code_status_dict['external_standard']['taskSnapshotId']
        # 保存草稿
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(
        #     self.tb_token, self.ctoken)
        # url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        templateStr = {
             "subtemp_2_group_1_1_mediaset": subtemp_2_group_1_1_mediaset,
             "subtemp_2_2_group_1_mediaset": subtemp_2_2_group_1_mediaset,
             "subtemp_2_3_group_1_mediaset": subtemp_2_3_group_1_mediaset,
             "subtemp_2_4_group_1_mediaset": subtemp_2_4_group_1_mediaset,
             "subtemp_2_5_group_1_mediaset": subtemp_2_5_group_1_mediaset,
             "subtemp_2_6_group_1_mediaset": [{"videoOfPackedAndLabeled01": {"value": "", "title": "包装贴标视频", "url": ""}},
                                              {"videoOfPackedAndLabeledOption02": {"value": "", "title": "包装贴标视频", "url": ""}},
                                              {"videoOfPackedAndLabeledOption03": {"value": "", "title": "包装贴标视频", "url": ""}}],
             "subtemp_2_7_group_1_textarea": subtemp_2_7_group_1_textarea
        }


        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO": {"taskId": taskId, "version": version},
                                "templateStr": json.dumps(templateStr), "taskSnapshotId": taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(
            self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 发货信息采集
    def get_information(self, url):
        subtemp_2_4_group_1_textarea = self.express_info
        taskId = self.code_status_dict['get_information']['taskId']
        version = self.code_status_dict['get_information']['version']
        taskSnapshotId = self.code_status_dict['get_information']['taskSnapshotId']
        templateStr = {
            "subtemp_2_3_group_1_mediaset": [{"videoLogisticFowarderTookAllTheProducts01": {"title": "包装贴标视频"}},
                                  {"videoLogisticFowarderTookAllTheProductsOption02": {"title": "物流发货视频"}},
                                  {"videoLogisticFowarderTookAllTheProductsOption03": {"title": "物流发货视频"}}],
            "subtemp_2_4_group_1_textarea": subtemp_2_4_group_1_textarea}
        data = {
            'json': json.dumps({"authTaskParamUpdateSimpleDTO": {"taskId": taskId, "version": version},
                                "templateStr": json.dumps(templateStr), "taskSnapshotId": taskSnapshotId})
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['referer'] = 'https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}'.format(
            self.order_id)
        response = requests.post(url, headers=headers, data=data, verify=False)
        print(response)
        print(response.text)

    # 数据库更新
    def update_database(self):
        url = 'https://onetouch.alibaba.com/moSurvey/schedule/list2.json?'
        params = {
            '_t': str(time.time()).replace('.', '')[:13],
            'json': json.dumps({"taOrderNo":str(self.order_id),"currentPage":1,"pageSize":10,"sort":{},"orderBy":"RANK","secondRankName":"tracking_service_warning_order","descSort":True})
        }
        url += urlencode(params)
        response = requests.get(url, headers=self.headers, verify=False)
        responseDatas = json.loads(response.text)['data']
        postUrl = 'http://py1.jakcom.it:5000/alibaba/post/order/update_process_info'
        datas = responseDatas['dataList']
        templateItemNameKey_dict = {"placeholder.expectFinishedDate": "请选择计划完成日期", "placeholder.remark": "请输入备注",
                                    "orderSchedule.task.templateName.taScheduleCloth.packageCompletion": "包装完成",
                                    "orderSchedule.task.templateName.taScheduleCloth.detectionCompletion": "检测完成",
                                    "orderSchedule.task.templateName.taScheduleCloth.materialPreparing": "备料入仓",
                                    "orderSchedule.task.templateName.taScheduleCloth.productionCompletion": "生产完成",
                                    "orderSchedule.task.templateName.taScheduleCloth.shipment": "出货",
                                    "orderSchedule.task.templateName.taScheduleCloth.productionStart": "生产开始",
                                    "orderSchedule.task.templateName.amzs.yangpin": "样品照片上传",
                                    "orderSchedule.task.templateName.amzs.dabaotiewaibia": "打包贴外标",
                                    "orderSchedule.task.templateName.amzs.dianshangziyuanbao": "电商资源包分享",
                                    "orderSchedule.task.templateName.amzs.tieneibia": "帖内标",
                                    "orderSchedule.task.templateName.amzs.jiancha": "检测完成",
                                    "orderSchedule.task.templateName.amzs.fahuo": "发货信息采集",
                                    "orderSchedule.task.templateName.taScheduleGeneral.detectionCompletion": "检测完成",
                                    "orderSchedule.task.templateName.taScheduleGeneral.packageCompletion": "包装完成",
                                    "orderSchedule.task.templateName.taScheduleGeneral.productionCompletion": "生产完成",
                                    "orderSchedule.task.templateName.taScheduleGeneral.shipment": "发货信息采集",
                                    "orderSchedule.task.templateName.taScheduleGeneral.shipment.button": "去发货",
                                    "orderSchedule.task.templateName.taScheduleGeneral.materialPreparing": "备料入仓",
                                    "orderSchedule.task.templateName.taScheduleGeneral.productionStart": "开始生产",
                                    "orderSchedule.task.templateName.loaded": "发货",
                                    "orderSchedule.task.templateName.knitting.zhuanghuo": "装货",
                                    "orderSchedule.task.templateName.knitting.xishui": "洗水",
                                    "orderSchedule.task.templateName.knitting.beiliao": "备料",
                                    "orderSchedule.task.templateName.knitting.fenghe": "套口缝合/手缝",
                                    "orderSchedule.task.templateName.knitting.baozhuang": "包装",
                                    "orderSchedule.task.templateName.knitting.bianzhi": "横机编织",
                                    "orderSchedule.task.templateName.knitting.houdao": "后道",
                                    "orderSchedule.task.templateName.3c.zhusu": "注塑",
                                    "orderSchedule.task.templateName.3c.baozhuang": "包装",
                                    "orderSchedule.task.templateName.3c.zhuanghuo": "装货",
                                    "orderSchedule.task.templateName.3c.tiepian": "贴片",
                                    "orderSchedule.task.templateName.3c.beiliao": "备料",
                                    "orderSchedule.task.templateName.3c.test": "老化测试",
                                    "orderSchedule.task.templateName.3c.zuzhuang": "组装",
                                    "orderSchedule.task.templateName.start30": "成品制定完成",
                                    "orderSchedule.task.templateName.start10": "布匹裁剪完成",
                                    "orderSchedule.task.templateName.clothing.zhuanghuo": "装货",
                                    "orderSchedule.task.templateName.clothing.houdao": "后道",
                                    "orderSchedule.task.templateName.clothing.baozhuang": "包装",
                                    "orderSchedule.task.templateName.clothing.beiliao": "备料",
                                    "orderSchedule.task.templateName.clothing.caifeng": "剪裁",
                                    "orderSchedule.task.templateName.clothing.fengren": "缝纫",
                                    "orderSchedule.task.templateName.start50": "烫染完成",
                                    "orderSchedule.task.templateName.start": "开始",
                                    "orderSchedule.task.templateName.default.packing": "包装",
                                    "orderSchedule.task.templateName.default.progressA": "生产A",
                                    "orderSchedule.task.templateName.default.progressB": "生产B",
                                    "orderSchedule.task.templateName.default.start": "备料",
                                    "orderSchedule.task.templateName.default.loading": "装货",
                                    "orderSchedule.task.templateName.finish": "打包装箱完成",
                                    "orderSchedule.task.buyer.view": "此环节买家查看次数",
                                    "orderSchedule.taOrderList.tracking_service_finished": "已完成",
                                    "orderSchedule.taOrderList.paymentStatus.ADVANCE": "预付款",
                                    "orderSchedule.taOrderList.paymentStatus.FULL": "全款",
                                    "orderSchedule.taOrderList.paymentStatus.BALANCE": "未付款",
                                    "orderSchedule.taOrderList.tracking_service_wait_for_checking": "进行中",
                                    "orderSchedule.firstLevel.desc.Agriculture": "农业",
                                    "orderSchedule.firstLevel.desc.Machinery": "机械",
                                    "orderSchedule.firstLevel.desc.Electrical_Equipment_Supplies": "电气设备及用品",
                                    "orderSchedule.firstLevel.desc.Lights_Lighting": "灯光和照明",
                                    "orderSchedule.firstLevel.desc.Office_School_Supplies": "办公文教用品",
                                    "orderSchedule.firstLevel.desc.Fashion_Accessories": "时尚饰品",
                                    "orderSchedule.firstLevel.desc.Chemicals": "化学物质",
                                    "orderSchedule.firstLevel.desc.Apparel": "服装",
                                    "orderSchedule.firstLevel.desc.Minerals_Metallurgy": "矿产和冶金",
                                    "orderSchedule.firstLevel.desc.Health_Medical": "健康与医疗",
                                    "orderSchedule.firstLevel.desc.Business_Services": "商业服务",
                                    "orderSchedule.firstLevel.desc.Sports_Entertainment": "体育和娱乐",
                                    "orderSchedule.firstLevel.desc.Fabrication_Services": "制造服务",
                                    "orderSchedule.firstLevel.desc.Textiles_Leather_Products": "纺织及皮革制品",
                                    "orderSchedule.firstLevel.desc.Food_Beverage": "食品和饮料",
                                    "orderSchedule.firstLevel.desc.Rubber_Plastics": "橡塑原料及制品",
                                    "orderSchedule.firstLevel.desc.Beauty_Personal_Care": "美容及个人护理",
                                    "orderSchedule.firstLevel.desc.Service_Equipment": "维修设备",
                                    "orderSchedule.firstLevel.desc.Furniture": "家具",
                                    "orderSchedule.firstLevel.desc.Gifts_Crafts": "礼品和工艺品",
                                    "orderSchedule.firstLevel.desc.Timepieces_Jewelry_Eyewear": "钟表、珠宝、眼镜",
                                    "orderSchedule.firstLevel.desc.Construction_Real_Estate": "建筑与房地产",
                                    "orderSchedule.firstLevel.desc.Electronic_Components_Supplies": "电子元件及用品",
                                    "orderSchedule.firstLevel.desc.Home_Appliances": "家用电器",
                                    "orderSchedule.firstLevel.desc.Luggage_Bags_Cases": "行李，袋子和箱子",
                                    "orderSchedule.firstLevel.desc.Packaging_Printing": "包装与印刷",
                                    "orderSchedule.firstLevel.desc.Toys_Hobbies": "玩具",
                                    "orderSchedule.firstLevel.desc.Environment": "环境",
                                    "orderSchedule.firstLevel.desc.Vehicles_Accessories": "车辆及配件",
                                    "orderSchedule.firstLevel.desc.Home_Garden": "家居与园艺",
                                    "orderSchedule.firstLevel.desc.Telecommunications": "电信",
                                    "orderSchedule.firstLevel.desc.Energy": "能源",
                                    "orderSchedule.firstLevel.desc.Security_Protection": "安全防护",
                                    "orderSchedule.firstLevel.desc.Shoes_Accessories": "鞋子和配件",
                                    "orderSchedule.firstLevel.desc.Consumer_Electronics": "消费电子",
                                    "orderSchedule.firstLevel.desc.Tools_Hardware": "工具和硬件",
                                    "orderSchedule.taskStatus.task_finished": "完成",
                                    "orderSchedule.taskStatus.wait_for_checking": "等待中",
                                    "orderSchedule.taskStatus.task_fail": "无法办理",
                                    "orderSchedule.taskStatus.all": "全部",
                                    "orderSchedule.produceProgressStatus.shipping_finish": "-",
                                    "orderSchedule.produceProgressStatus.order_finish": "-",
                                    "orderSchedule.produceProgressStatus.warning": "预警",
                                    "orderSchedule.produceProgressStatus.delay": "超期",
                                    "orderSchedule.produceProgressStatus.normal": "正常",
                                    "orderSchedule.reviewTaskStatus.wait_for_feedback": "待反馈",
                                    "orderSchedule.reviewTaskStatus.finish_evaluate": "已评价",
                                    "orderSchedule.reviewTaskStatus.wait_for_evaluate": "未评价",
                                    "orderSchedule.reviewTaskStatus.finished": "已反馈",
                                    "orderSchedule.rejectReason.image_not_true": "虚假拍摄",
                                    "orderSchedule.rejectReason.other_reason": "其他原因",
                                    "orderSchedule.rejectReason.location_distance_terrible": "地址偏差过大",
                                    "orderSchedule.rejectReason.inventory_product": "产品是库存产品",
                                    "orderSchedule.rejectReason.not_suit_for_order": "拍摄内容与订单不符",
                                    "orderSchedule.rejectReason.over_produt_time": "实际生产进度已超过当前阶段",
                                    "orderSchedule.rejectReason.image_or_video_not_uploaded": "未上传图片或视频",
                                    "orderSchedule.rejectReason.uploaded_image_or_video_unqualified": "已上传图片或视频不合格",
                                    "orderSchedule.rejectReason.no_enough_photo_employee": "未能安排拍摄人员",
                                    "orderSchedule.rejectReason.schedule_dely": "进度延期",
                                    "orderSchedule.rejectReason.not_ship_to_specified_warehouse": "未发货至指定海外仓",
                                    "orderSchedule.fail.mustLogin": "必须先登录才能操作",
                                    "orderSchedule.fail.noPermision": "无权操作该信保单",
                                    "orderSchedule.fail.paramError": "参数错误", "orderSchedule.fail.sysException": "系统异常",
                                    "orderSchedule.feedbackStatus.finished": "已反馈",
                                    "orderSchedule.feedbackStatus.wait_for_feedback": "待反馈",
                                    "orderSchedule.detail.product.name": "产品名称",
                                    "orderSchedule.detail.product.quantity": "数量",
                                    "orderSchedule.detail.product.description": "描述",
                                    "ta.schedule.task.template.resolver.eCommerceService": "电商一站通",
                                    "ta.schedule.task.template.resolver.eCommerceService.desc": "从定制、检测、打包贴标到发货一站式服务",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral": "生产可视化",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral.simple": "生产可视化",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral.desc": "生产型订单监控",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral.closed": "The order has been closed and order tracking service is not available. \n",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral.simpleMode.desc": "生产可视化简易模版描述",
                                    "ta.schedule.task.template.resolver.taScheduleGeneral.defaultMode.desc": "生产可视化模版描述",
                                    "ta.schedule.task.template.resolver.1200000212": "生产可视化",
                                    "ta.schedule.task.template.resolver.default": "默认类型",
                                    "ta.schedule.task.template.resolver.clothing": "服装",
                                    "ta.schedule.task.template.resolver.3c": "消费电子",
                                    "ta.schedule.task.template.resolver.knitting": "针织工艺",
                                    "ta.schedule.task.template.type": "可视化类型",
                                    "ta.schedule.page.createOrder.buyer.deliver.content": "供应商已发货，服务无法开启，更多了解",
                                    "ta.schedule.page.createOrder.buyer.deliver.content.rax": "供应商已发货，服务无法开启。",
                                    "ta.schedule.page.createOrder.buyer.deliver.title": "提示",
                                    "ta.schedule.page.createOrder.seller.deliver.content": "货物已发出，服务不能被开启。请在发货前开启订单可视化服务。",
                                    "ta.schedule.ta.order.relative.prepayment.expect.shipping.time": "预付款收齐到账duration天后发货",
                                    "ta.schedule.ta.order.relative.prepayment.expect.deliveryTime": "计划发货时间",
                                    "ta.schedule.ta.order.relative.prepayment.expect.deliveryStatus": "发货状态",
                                    "ta.schedule.ta.order.relative.prepayment.deliveryTime": "实际发货时间",
                                    "ta.schedule.ta.order.relative.all.payment.expect.shipping.time": "全款到账收齐duration天后发货",
                                    "ta.schedule.ta.order.relative.balance.payment.expect.shipping.time": "全款收齐后duration天后发货",
                                    "seller.show.buyer.view.num": "买家访问次数", "rax.buyer.submitted": "供应商已敦促及时上传最新生产情况。",
                                    "rax.buyer.header.title": "生产服务跟进",
                                    "rax.buyer.header.content.second": "如果延期仍未收到状态更新，或有其他问题，请联系供应商。",
                                    "rax.buyer.header.content.first": "供应商将按约定生产线上传图片。",
                                    "rax.buyer.header.confirmed": "待卖家确认",
                                    "rax.buyer.leave.comment": "联系供应商",
                                    "rax.buyer.select.tracking.steps": "选择生产跟进服务类型（多选）",
                                    "rax.buyer.select.one.multiple": "请选择一个或多个选项",
                                    "rax.buyer.preview.tracking": "预览生产跟进步骤",
                                    "rax.buyer.service.enabled": "服务未开启，联系供应商或者去PC端开启服务。",
                                    "rax.buyer.estimated.time": "预计完成时间",
                                    "rax.buyer.review": "评价",
                                    "rax.buyer.reminderText": "Note that order tracking only begins once initial payment has been made. ",
                                    "rax.buyer.remind.supplier": "提醒供应商",
                                    "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].IN_SHIPPING": "发货中",
                                    "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].WAIT_TO_SHIPPING": "等待发货",
                                    "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].BUYER_SIGN": "买家签收",
                                    "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].CLOSE": "订单关闭",
                                    "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].FINISH": "发货完成",
                                    "deliveryCenter.deliveryHome.deliveryStatus.ENUM].SELLER_SIGN": "卖家签收"}
        for data in datas:
            taOrderNo = data['taOrderNo']  # 信单保号
            buyerName = data['buyerName']  # 买家名称
            gmtCreate = data['gmtCreate']  # 创建时间
            templateItemNameKey = templateItemNameKey_dict.get(data['templateItemNameKey'], '未获取到样品状态')  # 样品状态
            localTime = data['expectShippingTime']
            expectShippingTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                int(str(localTime)[:10]))) if localTime is not None else ''  # 计划发货时间
            status = templateItemNameKey_dict.get('orderSchedule.taOrderList.' + data['status'], '未获取到办理状态')  # 办理状态
            currentOwner = data['currentOwner']  # 当前负责人
            buyerViewOrNot = '是' if data['buyerViewOrNot'] is True else '否'  # 买家是否查看
            paymentStatusKey = templateItemNameKey_dict[data['paymentStatusKey']]  # 付款状态
            produceProgressStatus = templateItemNameKey_dict.get(
                'orderSchedule.produceProgressStatus.' + data['produceProgressStatus'], '未获取到进度提醒')  # 进度提醒
            gmtTaskExpectFinished = data['gmtTaskExpectFinished'] if data[
                                                                         'gmtTaskExpectFinished'] is not None else ''  # 当前节点计划完成时间
            postData = {
                'Account': self.account,
                'TA_Order_ID': taOrderNo,
                'Buyer_Name': buyerName,
                'Create_Time': gmtCreate,
                'Progress_Rate': templateItemNameKey,
                'Sent_Time': expectShippingTime,
                'Process_Status': status,
                'Principal': currentOwner,
                'View_Status': buyerViewOrNot,
                'Remind_Status': produceProgressStatus,
                'Step_Time': gmtTaskExpectFinished,
                'Payment_Status': paymentStatusKey
            }
            print(postData)
            postResponse = requests.post(postUrl, postData)
            print(postResponse)
            print(postResponse.text)

    # 类的主函数
    def main(self):
        # 保存草稿
        draft_url = 'https://onetouch.alibaba.com/moSurvey/seller/saveSplitTaskDraft.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        # 提交给买家
        buyer_url = 'https://onetouch.alibaba.com/moSurvey/seller/commitToBuyerTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        # 结束此环节
        end_url = 'https://onetouch.alibaba.com/moSurvey/seller/commitAndEndTask.json?_tb_token_={}&ctoken={}'.format(self.tb_token, self.ctoken)
        local_img_datas = self.get_local_img(self.sku)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 样品照片上传
        subtemp_2_group_1_1_mediaset = self.add_front_img(local_img_datas['picturesOfSampleProductsFront'])
        subtemp_2_2_group_1_mediaset = self.add_back_img(local_img_datas['picturesOfSampleProductsBack'])
        subtemp_2_3_group_1_mediaset = self.add_side_img(local_img_datas['picturesOfSampleProductsSide'])
        subtemp_2_4_group_1_mediaset = self.get_video(local_img_datas['videoOfSampleProducts'])
        # 保存草稿
        self.save_sample_photo(draft_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset)
        # 提交给买家
        self.save_sample_photo(buyer_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset,subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset)
        # 结束此环节
        self.save_sample_photo(end_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset,subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 电商资源分享
        subtemp_2_group_1_2_mediaset = self.add_resource_pack()
        self.save_resource_pack(draft_url, subtemp_2_group_1_2_mediaset)
        self.save_resource_pack(buyer_url, subtemp_2_group_1_2_mediaset)
        self.save_resource_pack(end_url, subtemp_2_group_1_2_mediaset)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 检测完成
        subtemp_2_group_1_1_mediaset = self.add_detail_img(local_img_datas['picturesOfProductsDetails'])
        subtemp_2_4_group_1_mediaset = self.add_product_report()
        self.save_detail_img(draft_url, subtemp_2_group_1_1_mediaset, subtemp_2_4_group_1_mediaset)
        self.save_detail_img(buyer_url, subtemp_2_group_1_1_mediaset, subtemp_2_4_group_1_mediaset)
        self.save_detail_img(end_url, subtemp_2_group_1_1_mediaset, subtemp_2_4_group_1_mediaset)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 贴内标
        subtemp_2_group_1_1_mediaset = self.add_close_shot()
        subtemp_2_2_group_1_mediaset = self.add_vision(local_img_datas['picturesOfAllLabeledProductsLongShot'])
        self.internal_standard(draft_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset)
        self.internal_standard(buyer_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset)
        self.internal_standard(end_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 贴外标
        subtemp_2_group_1_1_mediaset = self.add_packaged_product_img(local_img_datas['picturesOfPackingFinishedProduct'])
        subtemp_2_2_group_1_mediaset = self.add_product_stacking_img(local_img_datas['picturesOfFinishedProducts'])
        subtemp_2_3_group_1_mediaset = self.add_unsealed_img(local_img_datas['picturesOfPackedProducts'])
        subtemp_2_4_group_1_mediaset = self.add_sealed_img(local_img_datas['picturesOfLabeledBoxesOrPallets'])
        subtemp_2_5_group_1_mediaset = self.add_warehouse_label_img(local_img_datas['pictureOfProdcutsInPalletWithShippingLabels'])
        self.external_standard(draft_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset, subtemp_2_5_group_1_mediaset)
        self.external_standard(buyer_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset, subtemp_2_5_group_1_mediaset)
        self.external_standard(end_url, subtemp_2_group_1_1_mediaset, subtemp_2_2_group_1_mediaset, subtemp_2_3_group_1_mediaset, subtemp_2_4_group_1_mediaset, subtemp_2_5_group_1_mediaset)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 信息采集
        self.get_information(draft_url)
        self.get_information(buyer_url)
        self.get_information(end_url)
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 更新数据库
        self.update_database()


def main(account, order_id, sku, express_info):
    productionFollowUpDetails = ProductionFollowUpDetails(account, order_id, sku, express_info)
    productionFollowUpDetails.main()


if __name__ == '__main__':
    account = 'fb2@jakcom.com'
    order_id =  14293742501021368
    sku = 'BH3'
    express_info = 'unpaid'
    main(account, order_id, sku, express_info)