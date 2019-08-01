# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: updateProduct.py
@time: 2019/7/27 8:16
@desc: alibaba 在线产品修改
"""
import re
import sys
import json
import copy
import requests
from urllib.parse import parse_qs, unquote
from alibaba.public import Public


class ProductTemplateError(Exception):

    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorInfo = ErrorInfo

    def __str__(self):
        return self.errorInfo


class UpdateProduct(Public):
    def __init__(self, account):
        self.account = account
        super(UpdateProduct, self).__init__(self.account)

    # 获取价格
    def getPrice(self):
        url = 'http://cs1.jakcom.it/alibaba/Get_prices'
        response = requests.get(url)
        # print(response.json())
        priceDict = {
            i['sku']: {
                'dropship': i['dropship_en_usd'],
                'wholesale_5_usd':i['wholesale_5_usd'],
                'wholesale_100_usd': i['wholesale_100_usd'],
                'fob_3000_usd': i['fob_3000_usd']
            }
            for i in eval(response.text)
        }
        return priceDict

    # 获取xsrfToken
    def getXsrfToken(self, itemId):
        url = 'https://post.alibaba.com/product/publish.htm?itemId=' + itemId
        response = requests.get(url, headers=self.headers)
        self.xcrfToken = re.findall(re.compile(r"tokenValue: '(.*?)'", re.S), response.text)[0]
        self.cookie = self.cookie + ';XSRF-TOKEN=' + self.xcrfToken
        self.headers['cookie'] = self.cookie

    # 获取需要修改的产品参数
    def getUpdateData(self, itemId):
        url = 'http://cs1.jakcom.it/AlibabaProductManage/productmsg_by_productid'
        params = {
            'productId': itemId
        }
        response = requests.get(url, params=params)
        datas = response.json()
        catId = datas['categoryId']
        sku = datas['sku']
        productTitle = datas['productTitle']
        productId = datas['productId']
        productKeywords = datas['productKeyWords'].split(',')
        customAttr = {i.split(':')[0].strip():i.split(':')[1].strip() + '###{}'.format(datas['Custom_Attr'].split('\n').index(i)) if '$key' not in i else productKeywords[int(i.split(':')[1].strip()[-2:-1]) - 1] + '###{}'.format(datas['Custom_Attr'].split('\n').index(i)) for i in datas['Custom_Attr'].split('\n') }
        return catId, sku, productTitle, productId, productKeywords, customAttr

    # 获取类目模板
    def getCatidTemplate(self, catId, sku):
        url = 'http://cs1.jakcom.it/AlibabaProductManage/postdata_by_productid'
        params = {
            'account': self.account,
            'categoryid': catId,
            'sku': sku
        }
        response = requests.get(url, params=params)
        # print(unquote(response.text))
        try:
            data = parse_qs(response.text[1:-1].replace(r'\u0026', '&'))
            templateData = json.loads(data['jsonBody'][0])
        except Exception as e:
            msg = {
                'account': self.account,
                'catId': catId,
                'sku': sku
            }
            raise ProductTemplateError('没有获取到该模板 ' + json.dumps(msg, ensure_ascii=False))
        return templateData

    # 获取服务数据
    def getServiceData(self):
        url = 'http://cs1.jakcom.it/AlibabaProductManage/servicedata'
        response = requests.get(url)
        serviceData = response.json()
        return serviceData

    # 获取产品 颜色 尺寸 的属性
    def getProductAttr(self):
        url = 'http://cs1.jakcom.it/Purpose/skuinfo'
        response = requests.get(url)
        datas = response.json()
        skuAttr = {}
        oldSku = [
            'RDW',
            'ACR',
            '08CD',
            'BH2',
            'SE2'
        ]
        for data in datas:
            if data['Shortname'] in oldSku:
                continue
            if data['state'] is False:
                continue
            if data['Shortname'] in skuAttr.keys():
                    # print(data)
                if data['variation_size'] == '' and data['variation_color'] == '':
                    pass
                elif data['variation_size'] != ''and data['variation_size'].isdigit():
                    if data['variation_size'] not in skuAttr[data['Shortname']]['attr']:
                        skuAttr[data['Shortname']]['attr'].append(data['variation_size'])
                else:
                    if data['EN_standard'] not in skuAttr[data['Shortname']]['attr']:
                        skuAttr[data['Shortname']]['attr'].append(data['EN_standard'])
            else:
                if data['variation_size'] == '' and data['variation_color'] == '':
                    attr = dict(attr=[0])
                elif data['variation_size'] != '' and data['variation_size'].isdigit():
                    attr = dict(attr=[data['variation_size']])
                else:
                    attr = dict(attr=[data['EN_standard']])
                skuAttr[data['Shortname']] = attr
        return skuAttr

    # 获取图片地址
    def getImgPath(self, sku):
        accountDirectory = self.account.split('@')[0]
        url = 'http://192.168.1.190:5000/alibaba/MassPhoto/%s/%s/' % (accountDirectory, sku)
        response = requests.get(url)
        datas = {k: '/run/user/1000/gvfs/smb-share:server=192.168.1.98,share=公共共享盘/@ 电商文档/alibaba/自动上新素材/生成结果/' + accountDirectory + '/' + sku + '/' + v.split(r'\\')[-1] for k,v in eval(response.text)}
        print(datas)
        return datas

    # 获取上传后的链接
    def getUploadImgUrl(self, sku, itemId, imgPathDatas):
        imgDict = {
            'main_pic': self.uploadImg(sku, itemId, imgPathDatas['main_pic']),      # 主图
            # 'vice_pic1': self.uploadImg(sku, itemId, imgPathDatas['vice_pic1']),    # 描述图1
            # 'vice_pic2': self.uploadImg(sku, itemId, imgPathDatas['vice_pic2']),    # 描述图2
            # 'vice_pic3': self.uploadImg(sku, itemId, imgPathDatas['vice_pic3']),    # 描述图3
            # 'vice_pic4': self.uploadImg(sku, itemId, imgPathDatas['vice_pic4']),    # 描述图4
            # 'vice_pic5': self.uploadImg(sku, itemId, imgPathDatas['vice_pic5']),    # 描述图5
            # 'packing_pic': self.uploadImg(sku, itemId, imgPathDatas['packing_pic']),# 包装图
            'main_video': self.getVideoDatas(sku, '主图'),                          # 视频主图
            'vice_video': self.getVideoDatas(sku, '描述页'),                        # 视频描述图
        }
        return imgDict

    # 本地视频
    def getVideoPath(self, sku):
        data = {
            'main_video': r'\\192.168.1.98\公共共享盘\@ 电商文档\alibaba\自动上新素材\群发视频\%s\主图\%s主图-2.mp4' % (sku, sku),
            'vice_video': r'\\192.168.1.98\公共共享盘\@ 电商文档\alibaba\自动上新素材\群发视频\%s\描述页\%s描述页-2.mp4' % (sku, sku),
        }
        return data

    # 视频银行
    def getVideoDatas(self, sku, searchKeys, page=1):
        url = 'https://hz-productposting.alibaba.com/product/ajax_video.do?ctoken=' + self.get_ctoken()
        postData = {
            'event': 'fetchList',
            'page': page,
            'pageSize': '10',
            'status': 'all',
            'gmtCreate': '',
            'linkedCount': '',
            'subject': sku + searchKeys,
            'quality': '',
            'maxDuration': '',
            'minDuration': '',
            'maxFileSize': '',
            'minFileSize': '',
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        response = requests.post(url, headers=headers, data=postData)
        datas = response.json()['data']['videos']
        counts = response.json()['data']['count']
        for index, data in enumerate(datas):
            if sku in data['videoName'] and searchKeys in data['videoName']:
                if data['linkedCount'] < 20:
                    return data
        if page * 10 > counts:
            return '没有符合条件的%s视频, 可能是所有视频达到最大关联上限' % searchKeys
        page += 1
        return self.getVideoDatas(sku, searchKeys, page)

    # 上传图片
    def uploadImg(self,sku, itemId, imgPath):
        imgName = imgPath.split('\\')[-1]
        url = 'https://kfupload.alibaba.com/mupload'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Cache-Control": "no-cache",
            "Host": "kfupload.alibaba.com",
            "Origin": "https://post.alibaba.com",
            # "Content-Type":"multipart/form-data; boundary={}".format(boundry),
            "Pragma": "no-cache",
            "Referer": "https://post.alibaba.com/product/publish.htm?spm=a2747.manage.0.0.5db771d2Ndp0j7&itemId=" + itemId,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        }
        fr = open(imgPath, 'rb').read()
        print(imgPath)
        data = {
            'name': imgName,
            'scene': 'productImageRule',
        }
        fields = {
            'file': (imgName, fr, 'application/octet-stream')
        }
        response = requests.post(url, headers=headers, files=fields, data=data)
        return response.json()

    # 获取描述信息
    def getProductDetail(self, sku, title):
        url = 'http://py1.jakcom.it:5000/alibaba/post/product/mass_link_description'
        data = {
            'account': self.account,
            'sku': sku,
            'title': title
        }
        response = requests.post(url, data=data)
        return response.text

    # 修改 产品标题 产品关键词 自定义属性
    def changeProductTitle(self, title, productKeywords, customAttr, templateData):
        templateData['productTitle'] = title
        templateData['productKeywords'] = productKeywords
        customMoreProperty = [None] * 10
        for text, value in customAttr.items():
            customMoreProperty[int(value[-1])] = {'text': text, 'value': value.split('###')[0]}
        templateData['customMoreProperty'] = customMoreProperty
        return templateData

    # 修改价格
    def changeProductPrice(self, sku, priceDict, templateData):
        ladderPrice = [
            {'quantity': 1, 'price': priceDict[sku]['dropship']},
            {'quantity': 5, 'price': priceDict[sku]['wholesale_5_usd']},
            {'quantity': 100, 'price': priceDict[sku]['wholesale_100_usd']},
            {'quantity': 3000, 'price': priceDict[sku]['fob_3000_usd']},
        ]
        templateData['ladderPrice'] = ladderPrice
        templateData['marketSamplingPrice'] = priceDict[sku]['dropship']
        return templateData

    # 描述更新
    def changeProductDetail(self, productDetail, templateData):
        templateData['superText'] = productDetail
        return templateData

    # 服务更新
    def changeProductService(self, serviceData, templateData):
        templateData['customizedServices'] = serviceData['customizedServices']
        templateData['productVisible'] = serviceData['productVisible']
        templateData['produceVisualization'] = serviceData['produceVisualization']
        templateData['ecIntegration'] = serviceData['ecIntegration']
        return templateData

    # 修改图片信息
    def modifyImgDatas(self, templateData, imgDatas):
        imgOnlineDatas = templateData['scImages']['list']
        a = copy.deepcopy(imgOnlineDatas)
        # print(a[0])
        templateData['scImages']['list'][0]['fileURL'] = imgDatas['main_pic']['url'].split(':')[1]
        templateData['scImages']['list'][0]['imgURL'] = imgDatas['main_pic']['url'].split(':')[1] + '_100x100.jpg'
        # oldData['scImages']['list'][1]['fileURL'] = imgDatas['vice_pic1']['url'].split(':')[1]
        # oldData['scImages']['list'][1]['imgURL'] = imgDatas['vice_pic1']['url'].split(':')[1] + '_100x100.jpg'
        # oldData['scImages']['list'][2]['fileURL'] = imgDatas['vice_pic2']['url'].split(':')[1]
        # oldData['scImages']['list'][2]['imgURL'] = imgDatas['vice_pic2']['url'].split(':')[1] + '_100x100.jpg'
        # oldData['scImages']['list'][3]['fileURL'] = imgDatas['vice_pic3']['url'].split(':')[1]
        # oldData['scImages']['list'][3]['imgURL'] = imgDatas['vice_pic3']['url'].split(':')[1] + '_100x100.jpg'
        # oldData['scImages']['list'][4]['fileURL'] = imgDatas['vice_pic4']['url'].split(':')[1]
        # oldData['scImages']['list'][4]['imgURL'] = imgDatas['vice_pic4']['url'].split(':')[1] + '_100x100.jpg'
        # oldData['scImages']['list'][5]['fileURL'] = imgDatas['vice_pic5']['url'].split(':')[1]
        # oldData['scImages']['list'][5]['imgURL'] = imgDatas['vice_pic5']['url'].split(':')[1] + '_100x100.jpg'
        templateData['imageVideo']['videoId'] = imgDatas['main_video']['videoId']
        templateData['imageVideo']['coverUrl'] = imgDatas['main_video']['coverUrl']
        templateData['imageVideo']['duration'] = imgDatas['main_video']['duration']
        templateData['imageVideo']['videoName'] = imgDatas['main_video']['videoName']
        templateData['imageVideo']['mediaStatus'] = imgDatas['main_video']['mediaStatus']
        templateData['detailVideo']['videoId'] = imgDatas['vice_video']['videoId']
        templateData['detailVideo']['coverUrl'] = imgDatas['vice_video']['coverUrl']
        templateData['detailVideo']['duration'] = imgDatas['vice_video']['duration']
        templateData['detailVideo']['videoName'] = imgDatas['vice_video']['videoName']
        templateData['detailVideo']['mediaStatus'] = imgDatas['vice_video']['mediaStatus']
        return templateData

    # 检测产品最终得分
    def checkProductScore(self, catId, itemId, templateData):
        url = 'https://post.alibaba.com/product/asyncOpt.htm?optType=productQualityAsyncRender'
        data = {
            'catId': catId,
            'itemId': itemId,
            'jsonBody': json.dumps(templateData)
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['x-xsrf-token'] = self.xcrfToken
        # headers['cookie'] = 'x-gpf-render-trace-id=0bb3d9a015642035491493729e6cf0; ali_apache_id=11.179.217.87.1557109662927.980741.2; t=0ec389e5303cc4ad299e6c6d2807925d; cna=n4lWFZbRW2YCAbe/sh4Lxj33; gangesweb-buckettest=183.191.178.30.1557109697018.0; UM_distinctid=16a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432; _ga=GA1.2.1933742769.1557196023; last_ltc_icbu_icbu=cHdk; sc_g_cfg_f=sc_b_currency=CNY&sc_b_locale=en_US&sc_b_site=CN; uns_unc_f=trfc_i=safcps^bnv96bor^in7r61t0^1dec1uncc; _bl_uid=wgjgax5we38ksmuabe3vg8miw836; cn_1262570533_dplus=%7B%22distinct_id%22%3A%20%2216a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201561777908%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201561777908%2C%22initial_view_time%22%3A%20%221561775548%22%2C%22initial_referrer%22%3A%20%22https%3A%2F%2Fpost.alibaba.com%2Fproduct%2Fpublish.htm%3FcatId%3D5093099%22%2C%22initial_referrer_domain%22%3A%20%22post.alibaba.com%22%7D; __utma=226363722.1933742769.1557196023.1563261562.1563261562.1; __utmz=226363722.1563261562.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); acs_usuc_t=acs_rt=7ed7d2cbb48d4143a083b8cce16498f4; cookie2=1879435292a8c6ace568b56e8a66c965; _tb_token_=ee8353ee1016e; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1560769958437&x_user=CN|Ady|JAKCOM|cgs|222438073&no_popup_today=n; intl_locale=zh_CN; ali_apache_tracktmp=W_signed=Y; XSRF-TOKEN=bd0b9911-0902-48ca-b0b4-18149bb70a10; _csrf_token=1564192111666; _hvn_login=4; csg=e23e45a1; xman_us_t=ctoken=18bi5ndogjod8&l_source=alibaba&x_user=YA3eyuex13KSerhKfvdaz0RcL0+jMw/2A4pHGTBxrRg=&x_lid=cn1512437204&sign=y&need_popup=y; intl_common_forever=PO0BqiCD9F2XrIrTrLaDjNWW8oFm95HHxvNUe4LPS4qRKrv+E4bxM4XIHMhIq3BVvG5Ls9M38oxvHvUa0rbI25/Cp9hy5vx8abR27c8VVIU=; xman_f=86Y4zmbLpRKvDfCAay83+BZ9VU4BLMu3Sb2Qq42Fq+OoWpOZ0eNe7aD5u8tQ+BF3Pg6cnZsMct8vDnjXhUrhArhsagyy9c9wxBkX3DA+bgFqzVplvlTsdTuM9/q8u3KG+6LElm9dZeIhDAS4eCzGnjcUhCESuL1tMPPp5K42MQNE6Y5j5A1jc44tKefmp3XldHXg2kM9Wvhke8ohElVJrGm7zUXKGeKMrnbCeGBSOwWtDoSGZL6g8EQEdniUasPN+4gT85q7w3yJenasIL0bvQ77HwsofUdY5I+yiHzudCIeamhpORawDkD9z8gmsHNy81m+NIj1NnMqvlfxe9dJasJ+nCuAY91JEd2tdtwnvXCF3Qy3jpGlMkH6VdmMPHTSCjJhTbpaS14=; ali_apache_track=ms=|mt=3|mid=cn1512437204; JSESSIONID=C61BDC3806048608A6F379D90377EB32; xman_t=dCh6f4ek7XGW2G5tBGRDigUn7Iu9DLf41x7EVRzaO6kEOdhfNgbGMZCzNZBty/FO1sYIAo55EkcEe8CfIgb6RN57FWFmGZGDPt1/1aruqSdXvOOpfUWe5G3Xfq97ESHwUiScH0/7K3MUVMzcajAQjO8BzNNlhsnkS4mAeY2zK5mw4qNH+LzoU6uuF42LrQ22KUg0efy4YrV68ojrnGYiukkQB7t8HNhhesMKdHsiX6ns94cFHQiGcDCImoIT3TFYFHyfW15F0S6SDFMCVbOMeN8S02uJEATbyXmjnvO/vObbUNktgT13T/A3+xlYyz0UXIjznEufIKgxd+JeIS9aQRj0S2HV/mVAwdfPZv4GZ5Q/cXJ0JnBvWgrV6gVeIq1qs81V4YV7taBOnHrjWCxdpHfuvTAF3uISpT3O8bNWDvqSwJlc9ksfDXPTwn6GLU7T3GDl2Qh06S0Df1HKI5M5NdhJAe9fLziAMy1w9+Z+tJlfXK8Vh41v6/W57yZotx2mE1N46973agRVsXltUHBMlcYdPzBG+6ExPG9ZfYHKPEhUGYXMBOIBEYLCB9Y7NcCkpS1xKX1oyfd6RtIrO9MFfDcOnz01xJ++CHYJrPNOEbZM/MQ9+IGurYKvlUmTUaixoMzTebIx7IH4Wy9SReHlWJhFpmSY8QHMGUWt3KbkR6Ju0kninQxLew==; l=cBQ0s6OIvqLqg33XBOfZSuI8LS79ZIRb8sPzw4OgiICPOYX9fnwVWZ3McatpCnGVLsMvR3rCLlQLB7TSEPU6lbftn6i_KHGl.; isg=BNnZ4fAc4HP9Mr0grmC5abp26MVzzsyYp6m2N_uOlIB0AvuUQ7Ln6rZUAIbRumVQ'
        response = requests.post(url, headers=headers, data=data)
        productScore = response.json()['components']['productQuality']['props']['score']
        return productScore

    # 提交
    def submit(self, productTitle, sku, catId, itemId, templateData):
        url = 'https://post.alibaba.com/product/asyncOpt.htm?optType=productRiskCheckAsyncRender'
        url = 'https://post.alibaba.com/product/submit.json?step=step3'
        data = {
            'catId': catId,
            'itemId': itemId,
            'jsonBody': json.dumps(templateData)
        }
        headers = self.headers
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['x-xsrf-token'] = self.xcrfToken
        # headers['cookie'] = 'x-gpf-render-trace-id=0bb3d9a015642035491493729e6cf0; ali_apache_id=11.179.217.87.1557109662927.980741.2; t=0ec389e5303cc4ad299e6c6d2807925d; cna=n4lWFZbRW2YCAbe/sh4Lxj33; gangesweb-buckettest=183.191.178.30.1557109697018.0; UM_distinctid=16a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432; _ga=GA1.2.1933742769.1557196023; last_ltc_icbu_icbu=cHdk; sc_g_cfg_f=sc_b_currency=CNY&sc_b_locale=en_US&sc_b_site=CN; uns_unc_f=trfc_i=safcps^bnv96bor^in7r61t0^1dec1uncc; _bl_uid=wgjgax5we38ksmuabe3vg8miw836; cn_1262570533_dplus=%7B%22distinct_id%22%3A%20%2216a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201561777908%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201561777908%2C%22initial_view_time%22%3A%20%221561775548%22%2C%22initial_referrer%22%3A%20%22https%3A%2F%2Fpost.alibaba.com%2Fproduct%2Fpublish.htm%3FcatId%3D5093099%22%2C%22initial_referrer_domain%22%3A%20%22post.alibaba.com%22%7D; __utma=226363722.1933742769.1557196023.1563261562.1563261562.1; __utmz=226363722.1563261562.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); acs_usuc_t=acs_rt=7ed7d2cbb48d4143a083b8cce16498f4; cookie2=1879435292a8c6ace568b56e8a66c965; _tb_token_=ee8353ee1016e; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1560769958437&x_user=CN|Ady|JAKCOM|cgs|222438073&no_popup_today=n; intl_locale=zh_CN; ali_apache_tracktmp=W_signed=Y; XSRF-TOKEN=bd0b9911-0902-48ca-b0b4-18149bb70a10; _csrf_token=1564192111666; _hvn_login=4; csg=e23e45a1; xman_us_t=ctoken=18bi5ndogjod8&l_source=alibaba&x_user=YA3eyuex13KSerhKfvdaz0RcL0+jMw/2A4pHGTBxrRg=&x_lid=cn1512437204&sign=y&need_popup=y; intl_common_forever=PO0BqiCD9F2XrIrTrLaDjNWW8oFm95HHxvNUe4LPS4qRKrv+E4bxM4XIHMhIq3BVvG5Ls9M38oxvHvUa0rbI25/Cp9hy5vx8abR27c8VVIU=; xman_f=86Y4zmbLpRKvDfCAay83+BZ9VU4BLMu3Sb2Qq42Fq+OoWpOZ0eNe7aD5u8tQ+BF3Pg6cnZsMct8vDnjXhUrhArhsagyy9c9wxBkX3DA+bgFqzVplvlTsdTuM9/q8u3KG+6LElm9dZeIhDAS4eCzGnjcUhCESuL1tMPPp5K42MQNE6Y5j5A1jc44tKefmp3XldHXg2kM9Wvhke8ohElVJrGm7zUXKGeKMrnbCeGBSOwWtDoSGZL6g8EQEdniUasPN+4gT85q7w3yJenasIL0bvQ77HwsofUdY5I+yiHzudCIeamhpORawDkD9z8gmsHNy81m+NIj1NnMqvlfxe9dJasJ+nCuAY91JEd2tdtwnvXCF3Qy3jpGlMkH6VdmMPHTSCjJhTbpaS14=; ali_apache_track=ms=|mt=3|mid=cn1512437204; JSESSIONID=C61BDC3806048608A6F379D90377EB32; xman_t=dCh6f4ek7XGW2G5tBGRDigUn7Iu9DLf41x7EVRzaO6kEOdhfNgbGMZCzNZBty/FO1sYIAo55EkcEe8CfIgb6RN57FWFmGZGDPt1/1aruqSdXvOOpfUWe5G3Xfq97ESHwUiScH0/7K3MUVMzcajAQjO8BzNNlhsnkS4mAeY2zK5mw4qNH+LzoU6uuF42LrQ22KUg0efy4YrV68ojrnGYiukkQB7t8HNhhesMKdHsiX6ns94cFHQiGcDCImoIT3TFYFHyfW15F0S6SDFMCVbOMeN8S02uJEATbyXmjnvO/vObbUNktgT13T/A3+xlYyz0UXIjznEufIKgxd+JeIS9aQRj0S2HV/mVAwdfPZv4GZ5Q/cXJ0JnBvWgrV6gVeIq1qs81V4YV7taBOnHrjWCxdpHfuvTAF3uISpT3O8bNWDvqSwJlc9ksfDXPTwn6GLU7T3GDl2Qh06S0Df1HKI5M5NdhJAe9fLziAMy1w9+Z+tJlfXK8Vh41v6/W57yZotx2mE1N46973agRVsXltUHBMlcYdPzBG+6ExPG9ZfYHKPEhUGYXMBOIBEYLCB9Y7NcCkpS1xKX1oyfd6RtIrO9MFfDcOnz01xJ++CHYJrPNOEbZM/MQ9+IGurYKvlUmTUaixoMzTebIx7IH4Wy9SReHlWJhFpmSY8QHMGUWt3KbkR6Ju0kninQxLew==; l=cBQ0s6OIvqLqg33XBOfZSuI8LS79ZIRb8sPzw4OgiICPOYX9fnwVWZ3McatpCnGVLsMvR3rCLlQLB7TSEPU6lbftn6i_KHGl.; isg=BNnZ4fAc4HP9Mr0grmC5abp26MVzzsyYp6m2N_uOlIB0AvuUQ7Ln6rZUAIbRumVQ'
        response = requests.post(url, headers=headers, data=data)
        print(response)
        print(response.text)
        logData = {
            'Account': self.account,
            'ProductID': itemId,
            'SKU': sku,
            'Subject': productTitle
        }
        self.log(logData)

    # 重新上传
    def restartImg(self, productTitle, sku, catId, itemId, templateData, times=0):
        if times >= 10:
            msg = {
                'account': self.account,
                'sku': sku,
                'catId': catId,
                'itemId': itemId
            }
            self.send_test_log(logName='alibaba在线产品修改', logType='Error', msg=json.dumps(msg, ensure_ascii=False), position='产品分数低于4.2分')
        times += 1
        imgPathDatas = self.getImgPath(sku)
        # 上传图片并获取上传后的地址
        imgDict = self.getUploadImgUrl(sku, itemId, imgPathDatas)
        templateData = self.modifyImgDatas(templateData, imgDict)
        productScore = self.checkProductScore(catId, itemId, templateData)
        # 最后总得分若大于4.2分, 则上传
        if float(productScore) > 4.2:
            self.submit(productTitle, sku, catId, itemId, templateData)
        # 最后总得分小于4.2, 重新上传图片
        else:
            return self.restartImg(productTitle, sku, catId, itemId, templateData, times)

    # 更新在线产品
    def updateProducts(self, itemId):
        self.getXsrfToken(itemId)
        # 获取价格
        print('获取价格')
        priceDict = self.getPrice()
        # step1 通过itemId 获取要修改的产品参数
        print('step1 通过itemId 获取要修改的产品参数')
        catId, sku, productTitle, productId, productKeywords, customAttr = self.getUpdateData(itemId)
        # step2 获取服务数据
        print('step2 获取服务数据')
        serviceData = self.getServiceData()
        # step3 获取需要修改的图片地址
        print('step3 获取需要修改的图片地址')
        imgPathDatas = self.getImgPath(sku)
        # 上传图片并获取上传后的地址
        """
        imgDict = self.getUploadImgUrl(sku, itemId, imgPathDatas)
        # step4 获取描述信息
        print('step4 获取描述信息')
        productDetail = self.getProductDetail(sku, productTitle)
        # step5 通过catId, account, sku 获取修改产品的类目模板
        print('step5 通过catId, account, sku 获取修改产品的类目模板')
        templateData = self.getCatidTemplate(catId, sku)
        # step6 修改标题 产品关键词 自定义属性
        print('step6 修改标题 产品关键词 自定义属性')
        templateData = self.changeProductTitle(productTitle, productKeywords, customAttr, templateData)
        # step7 修改价格
        print('step7 修改价格')
        templateData = self.changeProductPrice(sku, priceDict, templateData)
        # step8 描述更新
        print('step8 描述更新')
        templateData = self.changeProductDetail(productDetail, templateData)
        # step9 服务更新
        print('step9 服务更新')
        templateData = self.changeProductService(serviceData, templateData)
        # step10 主图 主图视频 描述视频更新
        print('step10 主图 主图视频 描述视频更新')
        templateData = self.modifyImgDatas(templateData, imgDict)
        # step11 总得分
        productScore = self.checkProductScore(catId, itemId, templateData)
        # 最后总得分若大于4.2分, 则上传
        if float(productScore) > 4.2:
            self.submit(productTitle, sku, catId, itemId, templateData)
        # 最后总得分小于4.2, 重新上传图片
        else:
            self.restartImg(productTitle, sku, catId, itemId, templateData)
        """
    # 日志
    def log(self, data):
        url = 'http://cs1.jakcom.it/AlibabaProductManage/modifyproduct_log'
        response = requests.post(url, data=data)
        print(response)
        print(response.text)

    def main(self, itemIds):
        for itemId in itemIds:
            try:
                self.updateProducts(itemId)
            except ProductTemplateError as p:
                self.send_test_log(logName='alibaba在线产品修改', logType='Error', msg=p,position='为获取到模板数据')
                continue
            except Exception as e:
                self.send_test_log(logName='alibaba在线产品修改', logType='Error', msg='%s %s %s' % (self.account, itemId, str(e)))
                continue


def main(account, itemIds):
    try:
        updateProduct = UpdateProduct(account)
        updateProduct.main(itemIds)
        return True
    except Exception as e:
        test_url = 'http://192.168.1.160:90/Log/Write'
        data = {
            'LogName': 'alibaba在线产品修改',
            'LogType': 'Error',
            'Position': '',
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': '%s %s %s' % (account, itemId, str(e)),
        }
        test_response = requests.post(test_url, data=data)
        print('test_response', test_response.text)



if __name__ == '__main__':
    account = 'tx@jakcom.com'
    itemId = ['62226669869']
    main(account, itemId)