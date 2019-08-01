# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: alibabaFan.py
@time: 2019/5/8 20:03
@desc:
"""
import re
import sys
import time
import random
import datetime
import json
import requests
import urllib
from urllib import parse, request


# from requests_toolbelt import MultipartEncoder
# from io import BytesIO


class AlibabaFan(object):
    def __init__(self, SKU, account):
        cookie_url = "http://192.168.1.99:90/alibaba/get_cookie_byaccount?platform=Alibaba"
        self.account = account
        self.cookie = self.get_cookie(cookie_url, account)
        # self.cookie = "ali_apache_id=11.179.217.87.1557109662927.980741.2; t=0ec389e5303cc4ad299e6c6d2807925d; cna=n4lWFZbRW2YCAbe/sh4Lxj33; gangesweb-buckettest=183.191.178.30.1557109697018.0; UM_distinctid=16a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432; sc_g_cfg_f=sc_b_locale=en_US; cookie2=1c173ba0bf6bfe1fae7710896e8dabc1; v=0; _tb_token_=fe678b3d3b877; acs_usuc_t=acs_rt=df4c8c47f18144f5bcb2a2b6802c1e9e; _ga=GA1.2.1933742769.1557196023; acs_rt=3b27dfd068c7401e960fed41c13bef46; XSRF-TOKEN=6c8535ce-051b-4d6a-98be-f9830aa58c06; _csrf_token=1557299353347; miniDialog=true; _gid=GA1.2.1182677803.1557469069; _m_h5_tk=af0a4943a3008eee7c18a4cd753917b7_1557478056315; _m_h5_tk_enc=39d99e61bcff893f33203a0ad3e8de03; ali_apache_tracktmp=W_signed=Y; intl_locale=zh_CN; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1557109691479&x_user=CN|Ady|Jakcom|cgs|230822478&no_popup_today=n; _hvn_login=4; csg=abb82f51; xman_us_t=ctoken=1ducwglpqzh32&l_source=alibaba&x_user=oJf0UJpOXEikCfRBMy22Nw86g2ggX6U7Q8uygkQNyI8=&x_lid=jakcomb2b&sign=y&need_popup=y; intl_common_forever=OLM9x9hYsyS9kEr4jndwbZxCy6gTpG1AZy6crLsgNz7/3W1q17DD6A==; xman_f=WO3osoZuUs6dNFqfwNT80Hp3qVTdQIhrSSfn0I7Z55zOUepEfKxs2HkTQQpwLjOYnYPYqDnlts/e23VzWxS2cdsu2rVe5YvEx3qGZuwSqm9UYHAGfcVmGeypSFWD6KEWFBEyVSuATNHC0/HRRPIedEBVVu6P1Jo4tHhiniiyia/ofF0YVqjyRukESv+nzQHAZY/xTBK6bvIVHVy0LRUy8v7r/RlU1sVThqGBhl89iVdMETSH6NoRMrhjHQmOAa/lkgrUGdynmvdjbxIInTt73SRPs5VQfw/DffzPZ+ua0T1rJTV2IVO6BldAajLm24c0K56zNEBWv6EyuZshi/M+wXFcpNQklgfJ+bmT7aXLZo76QzmSyF22J4aCDoWXL4NO; ali_apache_track=mt=3|ms=|mid=jakcomb2b; xman_t=sohZA+pD1NslbeRqXZuaRMC5ICZ+ac29XxBizLPslxPWdvmSUpUayTI8pfEMCEj1Dhps4sjcGWcxK/2JhQX11X7j1TIaKJiDyFGXC1Ee/7YwKJZcDpHJoGjG6IgFW0qtZU/leJb4R+1GUE23WPWUKiBlC73GzMlhPLRKYY6NOQPETA4Y9Jrlq5vVJRtbVDm3WLf4jSZbEz2A0N2fY7boy2lZkDnftdCZEFFgQaOHnJKIBWmJiafAXEqGKwB7t8usUjNAtS66ZgmHsngtVNe6hKW71UlBNCgKDCDYJnU4Rnlqf8hvgm0xVXDZdu0rvutq3ftrHCwDE46ZEzbDmPPxL8G55/3EIOwQc8PMQiaGT9O/K7PvtNmH4HmDhYvdNnUyailsi9SftMPk4XfuDqXXhUNEHP2xSEUhndiOF1bfd+IPlsMfLKmuKQ6iEtFu7h36/0AecSnBrMTHmRJUOxnfZ8h7IKKG1gHjXAnsaNa6rsYLXXsB32CRymNfjCA/nvalmBliqc960h/tPzEMDPL1j4mjFNzQ8IujmRPK5vXQQs6W9o/tM1FQpQg4atotfK1bp7Ieemj5q1aIHbUyGk9aS9+3s79TYzWzgzhnF56+ITiPZBfv1ZUIiJ/u0pQiu/HFHCyJHqOnUlvUSxo82ApP+8DPoRQOB/KLiGvRy+Wnoqls9u/68wUrhA==; l=bBI6KHolvDecmVb2BOCNIuI8LS7OSIRAguPRwCbDi_5aU6L1wu7OlL85dFp6Vj5R_qTB4UaStkw9-etki; isg=BJiYNoEOcK0txVwwP1K2cU8bacbqKf2L1mU8xdKJ5FOGbThXepHMm65HpeV4_bTj"
        ctoken_re_complie = re.compile(r"ctoken=(.*?)&", re.S)
        tb_token_re_complie = re.compile(r"_tb_token_=(.*?);", re.S)
        self.ctoken = re.findall(ctoken_re_complie, self.cookie)[0]
        self.tb_token = re.findall(tb_token_re_complie, self.cookie)[0]
        print('++' * 50, self.tb_token)
        self.feed_num_list = [i for i in range(13)]
        self.video_data = self.get_video(SKU)
        self.image_data = self.get_image(SKU)
        self.formData = self.get_formData()

    def get_cookie(self, url, account):
        """
        获取cookie
        :param url: 获取cookie 的链接
        :param account: 需要获取指定账号的cookie
        :return: 对应账户所需要的cookie
        """
        response = requests.get(url)
        cookies = json.loads(response.text)
        cookie_dic = {}
        for cookie in cookies:
            # 初始化cookie
            custom_cookie = ""
            # 便利cookie信息
            for i in eval(cookie["cookie_dict_list"]):
                # 拼接cookie
                custom_cookie = custom_cookie + i["name"] + "={}; ".format(i["value"])
            # 以键值对的形式存放到字典中
            cookie_dic[cookie["account"]] = custom_cookie.strip()
        # 返回指定cookie
        return cookie_dic[account]

    def get_headers(self, use):
        headers = {
            # "authority": "hz-productposting.alibaba.com",
            # "path": "/product/videobank/home.htm?spm=a2700.7756200.0.0.48f371d2PMraUq",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
            "cache-control": "max-age=0",
            "cookie": self.cookie,
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        }
        if use == "get_video":
            headers["authority"] = "hz-productposting.alibaba.com"
            headers["method"] = "POST"
            headers["path"] = "/product/ajax_video.do?ctoken={}".format(self.ctoken)
            headers["origin"] = "https://hz-productposting.alibaba.com"
            headers[
                "referer"] = "https://hz-productposting.alibaba.com/product/videobank/home.htm?spm=a2700.7756200.0.0.48f371d2PMraUq"
            return headers
        elif use == "get_formData":
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Referer"] = "https://creator.alibaba.com/publish/post?from=feed&template=icbuVideo"
            return headers
        elif use == "get_image":
            headers["host"] = "message.alibaba.com"
            return headers
        elif use == 'get_mainId':
            headers['referer'] = 'https://photobank.alibaba.com/home/index.htm'
            return headers
        elif use == 'get_products_class':
            return headers
        elif use == "submit":
            headers["method"] = "POST"
            headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            headers["Origin"] = "https://creator.alibaba.com"
            headers["Referer"] = "https://creator.alibaba.com/publish/post?from=feed&template=icbuVideo"
            headers["X-Requested-With"] = "XMLHttpRequest"

    def get_video(self, SKU):
        print("正在获取视频")
        headers = self.get_headers("get_video")
        # url = "https://arms-retcode.aliyuncs.com/r.png?t=api&times=1&page=hz-productposting.alibaba.com%2Fproduct%2Fvideobank%2Fhome.htm&tag=&begin=1557370835920&api=%2Fproduct%2Fajax_video.do&success=1&time=654&code=200&msg=&traceId=&sid=0Xj0CvChg5F1kjxqgxRFuzmdXj2I&sr=1920x1080&vp=585x937&ct=4g&uid=jqjdRvhhfmn0F5ijwkypan8gdsn8&pid=iw0okbwm8i%40a200e2aaa01bd1c&_v=1.5.4&sampling=1&z=jvg1xxuh"
        # r = requests.head(url, headers=headers)
        url = "https://hz-productposting.alibaba.com/product/ajax_video.do?ctoken={}".format(self.ctoken)
        print(url)
        data = {
            "event": "fetchList",
            "status": "all",
            "gmtCreate": "",
            "linkedCount": "",
            "page": "1",
            "pageSize": "10",
            "canUpgrade": "",
            "subject": SKU,
            "quality": "",
        }
        response = requests.post(url, headers=headers, data=(data))
        # print(response.text)
        video_datas = json.loads(response.text)["data"]["videos"]
        # print(video_datas)
        video_data = random.choice(video_datas)
        print("视频获取成功")
        # print(video_data)
        # pass
        return video_data

    def get_mainId(self):
        url = 'https://photobank.alibaba.com/photobank/node/ajax/groups/-1.do?ctoken={}&dmtrack_pageid=ddcc71460b0fd96b5cd5148016aa0584e0a224a604&_={}'.format(
            self.ctoken, str(time.time()).replace('.', '')[:13])
        headers = self.get_headers('get_mainId')
        response = requests.get(url, headers=headers)
        # print(response.text)
        datas = json.loads(response.text)
        for data in datas['object']:
            if data['name'] == '活动主图':
                return data['id']

    def get_image(self, SKU):
        print("正在获取封面图片")
        id = self.get_mainId()
        # print(id)
        url = "https://message.alibaba.com/message/content/material/pagePhotoBank.htm?pageSize=40&current=1&categoryId={}".format(
            id)
        # print(url)
        headers = self.get_headers("get_image")
        response = requests.get(url, headers=headers)
        image_datas = json.loads(response.text)
        image_data_dict = {}
        for image_data in image_datas["data"]["itemList"]:
            sku = image_data["title"].split("_")[0]
            if sku in image_data_dict.keys():
                image_data_dict[sku].append(image_data)
            else:
                image_data_dict[sku] = [image_data]
        # print(image_data_dict)
        image_data = random.choice(image_data_dict[SKU])
        print("获取封面图片成功")
        return image_data

    def get_product_class_id(self):
        url = 'https://message.alibaba.com/message/content/material/productGroup.htm?activityId=0'
        headers = self.get_headers('get_products_class')
        response = requests.get(url, headers=headers)
        # print(response.text)
        datas = json.loads(response.text)
        products_class = {data['name']: data['id'] for data in datas['data']['itemList']}
        # print(products_class)
        # print(products_class['Hot sale'])
        class_id = products_class.get('Hot sale', None)
        if class_id == None:
            class_id = products_class['Hot Sale']
        return class_id

    def get_products(self, sku, SKUS_new):
        id = self.get_product_class_id()
        url = "https://message.alibaba.com/message/content/material/pageProduct.htm?pageSize=20&q={}&current=1&categoryId={}".format(
            sku, id)
        print(url)
        headers = self.get_headers("get_image")
        response = requests.get(url, headers=headers)
        # print(response.text)
        # product_datas = json.loads(response.text)["data"]["itemList"]
        try:
            product_datas = json.loads(response.text)["data"]["itemList"]
        except KeyError as e:
            print(e)
            print(json.loads(response.text)["data"])

            print('fffffffffffffffffff', self.account, url)
            sku = SKUS_new.pop(random.choice(range(len(SKUS_new))))
            return self.get_products(sku, SKUS_new)
        except TypeError as e:
            print(e)
            print(json.loads(response.text)["data"])
            sys.exit()
        # print(product_datas)
        product_data = random.choice(product_datas)
        return product_data

    def structure_formData(self, video, image, formData):
        print("正在构建表单")
        uploadTime = str(time.mktime(time.strptime(video["gmtCreate"], "%Y-%m-%d"))).split(".")[0] + "000"
        uploadVideoValues = [{
            "coverUrl": video["coverUrl"],
            # sku 图片
            "duration": video["duration"],
            "playUrl": "//cloud.video.taobao.com/play/u/2153292369/p/1/e/6/t/10300/{}.mp4".format(video["videoId"]),
            # sku 视频
            "title": video["videoName"],
            "uploadTime": uploadTime,
            "videoCoverUrl": image["url"],
            # sku 图片封面
            "videoId": video["videoId"]
        }]
        uploadCoverValues = [{
            "materialId": 0,
            "fileId": 0,
            "fileName": image["title"],
            "folderId": "0",
            "formatSize": "",
            "pix": "{}x{}".format(image["picHeight"], image["picWidth"]),
            "sizes": 0,
            "thumbUrl": "{}_200x200".format(image["url"]),
            # sku 图片封面 + _200x200
            "url": image["url"]
        }]
        addProductsValue = []
        SKUS_new = get_sku()
        SKUS_new.remove(SKU)
        nine_sku_list = random.sample(SKUS_new, 9)
        print("正在获取推荐产品")

        for count in range(1):
            sku = SKUS_new.pop(random.choice(range(len(SKUS_new))))
            product = self.get_products(sku, SKUS_new)
            # print(SKUS_new)
            pic_data = {
                "materialId": product["materialId"],
                "coverUrl": product["coverUrl"],
                "images": [], "itemId": product["id"], "price": 0,
                "resourceUrl": "",
                "rawTitle": product["title"],
                "title": product["title"],
                "addFrom": "MARTERIALS", "bizCode": "icbu"
            }
            addProductsValue.append(pic_data)
        print("推荐产品获取成功")
        class_feed = [
            {"parent": "Feed内容类型", "label": "新品发布", "value": "373016:355030", "checked": False, },
            {"parent": "Feed内容类型", "label": "询盘热品", "value": "373016:369002", "checked": False},
            {"parent": "Feed内容类型", "label": "交易热品", "value": "373016:373001", "checked": False, },
            {"parent": "Feed内容类型", "label": "性能评测", "value": "373016:373002", "checked": False, },
            {"parent": "Feed内容类型", "label": "产品清单", "value": "373016:369003", "checked": False, },
            {"parent": "Feed内容类型", "label": "产品展示", "value": "373016:373003", "checked": False, },
            {"parent": "Feed内容类型", "label": "促销打折", "value": "373016:373005", "checked": False, },
            {"parent": "Feed内容类型", "label": "实地勘厂", "value": "373016:373006", "checked": False, },
            {"parent": "Feed内容类型", "label": "生产工艺", "value": "373016:373007", "checked": False, },
            {"parent": "Feed内容类型", "label": "公司介绍", "value": "373016:373008", "checked": False, },
            {"parent": "Feed内容类型", "label": "仓储运输", "value": "373016:373010", "checked": False, },
            {"parent": "Feed内容类型", "label": "定制能力", "value": "373016:350030", "checked": False, },
            {"parent": "Feed内容类型", "label": "展会现场", "value": "373016:373015", "checked": False, },
            {"parent": "Feed内容类型", "label": "买家评价", "value": "373016:373013", "checked": False, }]
        class_feed_new = class_feed.copy()
        feed_num = self.feed_num_list.pop(random.choice(self.feed_num_list))
        feedValue = [class_feed_new[feed_num]["value"]]
        feedClass = class_feed_new[feed_num]["label"]
        class_feed_new[feed_num]["checked"] = True
        title = "{}-{}-{}".format(SKU, feedClass, str(datetime.datetime.now().date()).replace("-", ""))
        sellingPoint = "Products, accessories, packaging,  All-round free customization;\nNo minimum order quantity limit;\nNo increase in price;\n24 hours delivery."
        formData["children"][0]["props"]["value"] = title
        formData["children"][1]["props"]["value"] = sellingPoint
        # formData["children"][2]["props"]["value"] = json.dumps(uploadVideoValues, ensure_ascii=False)
        # formData["children"][3]["props"]["value"] = json.dumps(uploadCoverValues, ensure_ascii=False)
        # formData["children"][4]["props"]["value"] = json.dumps(addProductsValue, ensure_ascii=False)
        # formData["children"][5]["props"]["value"] = json.dumps(feedValue, ensure_ascii=False)
        # formData["children"][5]["props"]["dataSource"]["Feed内容类型"] = json.dumps(class_feed, ensure_ascii=False)
        formData["children"][2]["props"]["value"] = uploadVideoValues
        formData["children"][3]["props"]["value"] = uploadCoverValues
        formData["children"][4]["props"]["value"] = addProductsValue
        formData["children"][5]["props"]["value"] = feedValue
        formData["children"][5]["props"]["dataSource"]["Feed内容类型"] = class_feed
        # serverData = "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"
        # formData['formData']["serverData"] = serverData
        formData['formData']["publishToolbar"] = '[{"text":"发布新Feed"}]'

        print('1' * 100)
        print(formData.keys())
        print("表单构建成功")
        return formData

    def get_formData(self):
        print("正在获取表单")
        url = "https://cpub.alibaba.com/render.json?from=feed&template=icbuVideo"
        headers = self.get_headers("get_formData")
        response = requests.get(url, headers=headers)
        formData = json.loads(response.text)["config"]
        print('**--' * 20)
        print(response.text)
        print('**--' * 20)
        count = formData["actions"][1]["text"]
        print(count)
        print("表单获取成功")
        return formData

    def submit(self, formData):
        print("正在提交表单")
        # '''
        # url = "https://cpub.alibaba.com/submit.json"
        # url = "https://cpub.alibaba.com/submit.json?_tb_token_={}".format(self.tb_token)
        url = "https://cpub.alibaba.com/submit.json?draft=1&_draft_id=0&_tb_token_={}".format(self.tb_token)
        data = {"config": formData}
        print(data)
        headers = {
            'Host': 'cpub.alibaba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://creator.alibaba.com/publish/post?spm=a2116r.creation-new-seller.main.1.1417138cI66SWF&from=feed&template=icbuVideo',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': '21272',
            'Origin': 'https://creator.alibaba.com',
            'Cookie': self.cookie,
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        options_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            'Access-Control-Request-Headers': 'x-requested-with',
            'Access-Control-Request-Method': 'POST',
            # "Content-Length": "%s"%len(parse.urlencode(data)),
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Cookie": self.cookie,
            "Host": "cpub.alibaba.com",
            "Origin": "https://creator.alibaba.com",
            "Pragma": "no-cache",
            # "Referer": "https://creator.alibaba.com/publish/post?from=feed&template=icbuVideo",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
            # "X-Requested-With": "XMLHttpRequest",
        }

        data = str(data).replace('{"text":"发布新Feed"',r'{\"text\":\"发布新Feed\"').replace("'",'"')
        print(data)


        # r = requests.options(url, headers=options_headers)
        # print(r)
        # print(r.url)
        # print(r.headers)
        # print(r.reason)
        # print('+-+-+' * 20)
        # # data = str(data).replace("'",'"').replace('{"text":"发布新Feed"}',r'{\"text\":\"发布新Feed\"}')
        # # data = json.dumps(data)
        # # print(data)
        # # data = json.loads(data)
        # print(data)
        # data = parse.urlencode(data)
        # print(data)
        # response = requests.post(url, headers=headers, data=(data))
        # # response = requests.post('http://httpbin.org/post', headers=headers, data=(data))
        #
        # # print(url)
        # # print(data)
        # # print(response)
        # print(response.url)
        # print('-----')
        # print(response.headers)
        # print('-----')
        # print(response.text)
        # print('-----')
        # # req = urllib.request.Request(url, data=data, headers=headers)
        # # result = urllib.request.urlopen(req)
        # # print(result)


def get_sku():
    url = "http://192.168.1.99:90/alibaba/Get_tempurl_byaccount"
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


if __name__ == "__main__":

    SKUS = get_sku()
    print(SKUS)
    cookie_accounts = [
        # "fb1@jakcom.com",
        # "fb2@jakcom.com",
        "fb3@jakcom.com",
        # "tx@jakcom.com",
    ]
    for account in cookie_accounts:
        for i in range(1):
            SKU = SKUS.pop(random.choice(range(len(SKUS))))
            print(SKU)
            alibaba = AlibabaFan(SKU, account)
            formData = alibaba.structure_formData(alibaba.video_data, alibaba.image_data, alibaba.formData)
            # print(json.dumps(formData, ensure_ascii=False))
            print("\n" * 2)
            print("-*" * 200)
            alibaba.submit(formData)
#    tb_token
