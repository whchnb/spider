# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: shippingFaildOrder.py
@time: 2019/7/19 10:49
@desc: 物流问题订单
"""
import re
import time
import requests
from selenium import webdriver
from w3lib.html import remove_tags
from aliexpressNew.public import Public
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class ComplaintImgSelenium:
    # 类的初始化
    def __init__(self, cookie, url):
        """
        类的初始化
        """
        # 继承父类Public 的init 方法
        self.cookie = cookie
        # 请求目标链接
        self.url = url
        # 构造浏览器对象
        self.browser = self.launch_web()

    #  启动无头浏览器
    def launch_web(self):
        """
        启动无头浏览器
        :return: 浏览器对象
        """
        print('正在启动浏览器')
        # 浏览器设置
        chrome_options = Options()
        # 设置无头
        # chrome_options.add_argument('--headless')
        # 加上这个属性来规避bug
        chrome_options.add_argument('disable-gpu')
        # 设置浏览器分辨率
        chrome_options.add_argument('window-size=1200,1100')
        # 不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 配置浏览器
        # chrome_options.add_experimental_option("prefs", prefs)
        # 启动浏览器
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.maximize_window()
        # 使用浏览器打开链接
        browser.get(self.url)
        # 删除浏览器生成的cookie
        browser.delete_all_cookies()
        # 获取账户对应cookie
        cookie_list = self.cookie
        for cookie in cookie_list.split(';'):
            # 将cookie添加到浏览器中
            try:
                browser.add_cookie({'name': cookie.split('=')[0], 'domain': '.aliexpress.com',
                                    'value': ''.join(cookie.split('=')[1:])})
            except:
                pass
        print('cookie 更改成功')
        # 重新打开链接
        browser.get(self.url)
        return browser

    def screenshot(self):
        self.browser.find_element_by_tag_name('body').send_keys(Keys.DOWN)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.DOWN)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.DOWN)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.DOWN)
        self.browser.find_element_by_tag_name('body').send_keys(Keys.DOWN)
        self.browser.get_screenshot_as_file('shipping.png')

    def quit(self):
        self.browser.quit()


class ShippingFaildOrder(Public):
    def __init__(self, account):
        self.account = account
        super(ShippingFaildOrder, self).__init__(self.account)

    def getFaildOrder(self):
        url = 'https://ilogistics.aliexpress.com/warehouse_order_list.htm'
        data = {
            'page': '1',
            'tradeOrderId': '',
            'intlTrackingNo': '',
            'warehouseOrderId': '',
            'logisticsChannel': '',
            'warehouseCode': '',
            'logisticsStatus': 'send_goods_fail',
            'gmtStartStr': '',
            'gmtEndStr': '',
        }
        response = requests.post(url, headers=self.headers, data=data)
        orederDatas = re.findall(re.compile(r'<tbody class=".*?">(.*?)</tbody>', re.S), response.text)
        print(len(orederDatas))
        for orderData in orederDatas:
            shippingId = re.findall(re.compile(r'<strong>.*?\s*?(\d*?)\s*?</strong>', re.S), orderData)[0]
            shippingTrackId = re.findall(re.compile(r'<label>\s*(.*?)\s*</label>', re.S), orderData)[0]
            orderId = \
                re.findall(re.compile(r'<a href="//trade.aliexpress.com/order_detail.htm\?order_id=(.*?)">', re.S),
                           orderData)[0]
            shippingCompany = re.findall(re.compile(r'<td class="td-quantity" data="(.*?)">', re.S), response.text)[0]
            shippingCompanyId = re.findall(re.compile(r'</p><p>\s*?(.*?)\s*?</p>', re.S), orderData)[0]
            createDate = \
                re.findall(re.compile(r'<td align="left" colspan="3"><span>.*?:\s?([\d.:\s]*?)</span>', re.S),
                           orderData)[0]
            wareHouseData = remove_tags(
                re.findall(re.compile(r'<td class="td-preassigned-id">(.*?)</td>', re.S), orderData)[0])
            orderType = wareHouseData.strip().split('\n')[0]
            wareHouse = wareHouseData.strip().split('\n')[-1].strip()
            try:
                complaintUrl = re.findall(re.compile(r'\| <a\s*?href="(.*?)" target="_blank">', re.S), orderData)[0]
            except:
                continue
            shippingStatus = re.findall(re.compile(r'<span class="logistics-status">\s*(.*?)\s*</span>'), orderData)[0]
            print(shippingId)
            print(shippingTrackId)
            print(orderId)
            print(shippingCompany)
            print(shippingCompanyId)
            print(createDate)
            print(orderType)
            print(wareHouse)
            print(complaintUrl)
            print(shippingStatus)
            complaintUrl = 'https://ilogistics.aliexpress.com/' + complaintUrl
            print(complaintUrl)
            if complaintUrl is not None:
                shippingFaildUrl = 'http://track.aliexpress.com/logisticsdetail.htm?tradeId=' + orderId
                # print(shippingFaildUrl)
                self.complaint(shippingFaildUrl)
                self.submit(complaintUrl, shippingStatus)

    def submit(self, url, shippingStatus):
        # self.driver =  ComplaintImgSelenium(self.cookie, 'https://gsp.aliexpress.com/apps/order/index')
        self.driver.browser.get(url)
        time.sleep(2)
        # iframe_element = self.driver.browser.find_element_by_class_name('//*[@id="content"]/div/iframe')
        self.driver.browser.switch_to.frame(0)
        self.driver.browser.find_element_by_xpath('//*[@id="content"]/div[3]/div[1]/div/ul/li[1]/div/a').click()
        time.sleep(3)
        self.driver.browser.find_element_by_xpath('//*[@id="J_subReasonId"]').click()
        # reason = self.driver.browser.find_element_by_xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[2]/ul/li[3]/text()')
        # print(reason)
        self.driver.browser.find_element_by_xpath('//*[@id="J_subReasonId"]/option[3]').click()
        self.driver.browser.find_element_by_xpath('//*[@id="J_remark"]').send_keys(shippingStatus)
        self.driver.browser.find_element_by_xpath('//*[@id="alipayAccount"]').send_keys('13623627373')
        self.driver.browser.find_element_by_xpath('//*[@class="file-input"]').send_keys(r'D:\Main\aliexpressNew\shipping.png')
        self.driver.browser.find_element_by_xpath('//*[@id="J_form"]').click()
        time.sleep(2)
        try:
            self.driver.browser.find_element_by_xpath('//*[@id="auth-f7"]').send_keys('田旭')
            self.driver.browser.find_element_by_xpath('//*[@id="J_submit_btn"]').click()
        except Exception as e:
            time.sleep(3)
            self.driver.browser.find_element_by_xpath('//*[@id="auth-f7"]').send_keys('田旭')
            self.driver.browser.find_element_by_xpath('//*[@id="J_submit_btn"]').click()
            print(e)
        print('ok')

    def complaint(self, url):
        self.driver = ComplaintImgSelenium(self.cookie, 'https://gsp.aliexpress.com/apps/order/index')
        self.driver.browser.get(url)
        time.sleep(1)
        self.driver.screenshot()
        print('screen shot success')
        # complaintImg.quit()

    def test(self):
        url = 'https://login.aliexpress.com/iLogin.htm'
        params = {
            'goto': '//workstation.i56.taobao.com/complainSelect.htm?type=2&orderId=135656817434'
        }
        headers = self.headers
        headers['cookie'] = 'ali_apache_id=183.191.178.30.1557109691539.397124.9; _uab_collina=155775237657626892450789; cna=n4lWFZbRW2YCAbe/sh4Lxj33; UM_distinctid=16af89d82063ba-073d310012acd8-e353165-1fa400-16af89d8207d6; _ga=GA1.2.1476120754.1559380888; _fbp=fb.1.1560486273492.191198052; aefeMsite=amp-x33dk4ABeg4i2Wp6uq1J-g; AMP_ECID_GOOGLE=amp-7jJN43JwLTD_rVcyYRBbMQ; amp-user-notification=amp-TKdO9MxsPZGcsRqZEgixxg; aemsite=d_bar=1; aep_history=keywords%5E%0Akeywords%09%0A%0Aproduct_selloffer%5E%0Aproduct_selloffer%0932821558272%0933038431430%0932935349969%0932863058216%0932874337210%0933037046720%0932976751904%0932821558272; __utmz=3375712.1563000968.5.3.utmcsr=trade.aliexpress.com|utmccn=(referral)|utmcmd=referral|utmcct=/orderList.htm; _ym_uid=1563001361706108694; _ym_d=1563001361; aeu_cid=8982dfad44754e8d9bf87b79976c0fcd-1563253623825-08281-b6Jk1kus; aep_common_f=nZFGgi5R1afGyfZcoQaRB2B2P5XIp/mGVwqvkFL+XZ2P2Rivx13DxA==; _bl_uid=wOjkgyC87wkwqqfFq8RgsLqttz7U; _lang=zh_CN; __utma=3375712.1476120754.1559380888.1563279071.1563421495.11; acs_usuc_t=x_csrf=hrchrjyzsz3s&acs_rt=8242e951a6824c6caca0b21d79a5e411; _m_h5_tk=eb6fe30a40b361710389f6e581577053_1563588468634; _m_h5_tk_enc=5af904aa48313992e4141efe5d1bd96c; _gid=GA1.2.1416150430.1563579831; _hvn_login=13; xman_us_t=x_lid=jakcomtech&sign=y&x_user=zIDENBC3FIGBtpLpsOj5wITgUNb2VwqMZlwkQvFbH5Q=&ctoken=413d917re54a&need_popup=y&l_source=aliexpress; aep_usuc_t=ber_l=A0; xman_f=owWIIfSCBKA1TJ/M4/dIChxHLbRp7ExCkk9KEpI800egoMM/yw0K4GwN9f51nSCr6UEGF/NfuxBVVvkGOqipoa4+C6+g+yYNHCawlZvkMUt3HS69ZOtpGwMq3vDUG4TuaGcCStCuOzEwT8lGa/5US3H3cLmAg/7Oq4DGQoWxFDg7/JUrWip+Mk+wOVbrkTH+FGBpRg0kUgEvnK3rxw2GXAPPQnW+8W/xo7ujQiCM2YKNzqtUbIQ3OHboKf1Dk2KUNTAbGGuIwrPTlEozXv1gpMp59lbmUe7JR/hEoqplmW7Y75oTO6Rn7lPhRTRLGhycNX8ZANJ9j+BgzsbVNgIygjE7mzLZFiTDsfh98WGCMOlPkJA5jOVskVpdhyf1WhM8MeMZOC9CbgXaglQvFanLuA==; aep_usuc_f=isfm=y&site=glo&c_tp=USD&ispm=y&x_alimid=229737297&iss=y&s_locale=zh_CN&region=US&b_locale=en_US; ali_apache_tracktmp=W_signed=Y; xman_us_f=zero_order=y&x_locale=zh_CN&x_l=1&last_popup_time=1557109691567&x_user=CN|Ady|Cao|cnfm|229737297&no_popup_today=n&x_as_i=%7B%22aeuCID%22%3A%228982dfad44754e8d9bf87b79976c0fcd-1563253623825-08281-b6Jk1kus%22%2C%22af%22%3A%221890605309%22%2C%22affiliateKey%22%3A%22b6Jk1kus%22%2C%22channel%22%3A%22AFFILIATE%22%2C%22cn%22%3A%2210008100042%22%2C%22cv%22%3A%221%22%2C%22ms%22%3A%220%22%2C%22src%22%3A%22promotion%22%2C%22tagtime%22%3A1563253623825%7D; intl_locale=zh_CN; JSESSIONID=CC407D44341DE67A45273BF97DAE077D; ali_apache_track=ms=|mt=2|mid=jakcomtech; xman_t=S/BYOMriTXB9U+0hSVCJW+iC+z7Ji4pKsKTAf7N9uGxz2UxWqtZpWI6FiRbPp1D0WvgHtGqtlYkE+AVREu5rzlT99mYoDis4Hcj1pQ9jkq3IA6Tx1K3NskfQfCoNtn6jtv9vlzlVixofg3zsstUDYeeEAiQ4pJ2AWrVeM4WRlELDeOfY36ew9upne+6vvPjImKe6HpEjzQkV4fukZYVqsNI1g0Atm5PHZa8mA5JfwuChJg/j5stghQDc6ILtmQtEhDt7xOIXeogwgp2jBh0s2TCEFpbHQgI0gAVV/iV83dcG9D/0akbXqLEbXiNb5gg3oSI/pHKTsGKMswYg+B/GOGJBLnQY80oojEqvG310lAsQAK3PAYI+EOy6RfBudkvVjBb6C4F6vNQcSTSIkQNmzxTj9PlZtlv9yeDltBvKDU8SPU/AAWCg80H2qvSdCkybfYURtyNteg2IrGdt+YXWUKvuGLQxaVk3QK9I7rnpPU5TPQHBVgbK/wWB0elnBKRaLyARujblDt8mvSLv+RzlolrxJiFy5I/AAz2tFXZ1arhC6C9ZsehCGVaauzoZBMB/uzdsniy0WQeFzmt070z4QDvpxkmYnj4ST3O4z7IvGVNFx3hSIoe2O013kpy0iFbo4JniASmD7Mkfs254qbrJLQ==; intl_common_forever=3B2xTXmNrBfcOXMqzrPUDv0w7orik9qDk8z0wI4L06d1C8A4lLcdWg==; isg=BAYG7eBUpyOblHNEMmh9cIUhV_xIz0uhDFg5HvAv8ikE86YNWPeaMeyCz2-a20I5; l=cBPvuJ0RqSJPDZbOBOCNIuI8LS7OSIRAguPRwCbDi_5CU6T1XgQOkq-SgF96VjWdtsTB4k6UXwe9-etkwNYw82RKJEDF.'
        response = requests.get(url, headers=headers, params=params)
        print(response)
        print(response.text)
        print(response.headers['set-cookie'])
        # cookie = re.findall(re.compile(r'(\w*?)=(.*?);'), response.headers['set-cookie'])
        # print(cookie)
        # cookies = lambda i: set([a[0] for a in i])
        # print(111)
        # print(cookies(cookie))
        # cookies = 'hl_sk=kGvnPSrgL-bAaYaiQbbIKw; havana_tgc=eyJjcmVhdGVUaW1lIjoxNTYzNjE0NzE5NzU3LCJudWxsIjpmYWxzZSwicGFydGlhbFRnY1ByZXNlbnQiOnRydWUsInBhdGlhbFRnYyI6eyJhY2NJbmZvcyI6eyIwIjp7ImFjY2Vzc1R5cGUiOjEsIm1lbWJlcklkIjozMDIxMDgzMjIzLCJ0Z3RJZCI6IjFIMVczLUgzcVMydnJMNnZRNFlZak93In19fSwidGdjUHJlc2VudCI6ZmFsc2V9;'

    def getCookie2(self):
        url = 'https://login.taobao.com/member/vst.htm'
        params = {
            'st': '1X9QWloJWudc92OrIrjFNog',
            'params': 'loginsite%3D0%26TPL_username%3Djakcomtech%26redirectURL%3D%252F%252Fworkstation.i56.taobao.com%252FcomplainSelect.htm%253Ftype%253D2%2526orderId%253D135656817434%26full_redirect%3Dfalse%26active%3Dfalse',
            'stEncrypt': 'null',
        }
        response = requests.get(url, headers=self.headers, params=params)
        cookie2 = re.findall(re.compile(r'cookie2=(.*?);'), str(response.headers))[0]
        return cookie2

    def getCode(self):
        url = 'https://workstation.i56.taobao.com/workOrderCommentRPC/uploadOSSAttach.json'
        headers = {
            'authority': 'workstation.i56.taobao.com',
            'method': 'GET',
            'path': '/workOrderCommentRPC/uploadOSSAttach.json',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            # 'cookie': 'cookie2=1ecfea726f56c7d4af6e3627e6af003c; sg=h39',
            'cookie': self.cookie,
            # 'cookie': 'cna=n4lWFZbRW2YCAbe/sh4Lxj33; thw=cn; t=1f71f19a13a626847bf3376cbfa1cbe0; tg=0; UM_distinctid=16af37216e72a1-03697f5b9d8c73-e353165-1fa400-16af37216e82ce; hng=CN%7Czh-CN%7CCNY%7C156; enc=q2AanCaDoQPIGYqLsStZXkJjkBeuhLSrx1DenIQJLXCHWCbt4uNQ%2BAPsVCrG8LV3uaIq6Oe9vj0XEnc9WpMn%2Bw%3D%3D; tracknick=jakcomtech; lgc=jakcomtech; _m_h5_tk=0ad56cb17962e10b1a7899694b9a1d5e_1563338963560; _m_h5_tk_enc=b3cfb01cb55b9cdb8c997ddac47e6ed7; mt=ci=-1_0&np=; cookie2=1ecfea726f56c7d4af6e3627e6af003c; _tb_token_=553e3b7e351de; v=0; dnk=jakcomtech; unb=3021083223; uc1=cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21=UtASsssmeW6lpyd%2BAHnb&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie14=UoTaG7lCL7Es6w%3D%3D&tag=8&lng=zh_CN; sg=h39; _l_g_=Ug%3D%3D; skt=faf017f6d6491fff; cookie1=VWZ9JMuvBqZ0OUn7gwBGlrlfvIOnZ1k2rKB%2B7RkTlMY%3D; csg=a70fd743; uc3=vt3=F8dBy3zf%2FPlox4wuLrI%3D&id2=UNDWozrBZwR8pQ%3D%3D&nk2=CdKZzh132OkdAA%3D%3D&lg2=URm48syIIVrSKA%3D%3D; existShop=MTU2MzYxMTMxMQ%3D%3D; _cc_=VFC%2FuZ9ajQ%3D%3D; _nk_=jakcomtech; cookie17=UNDWozrBZwR8pQ%3D%3D; l=cBENZ7fmqapsGWKABOfaIuI8LS79mIRb8sPzw4OgiICPOxCp5hJNWZ3204Y9CnGVLswHR3rCLlQLBXLgJyUIhe5NTzm0cfXO.; isg=BC8v81aWrpTd4qq86moK0BT0vkP5fIJ2DdvAcUG8SB6lkE6SSadnRrcCEsAL6Ftu',
            'referer': 'https://workstation.i56.taobao.com/complain_post.htm?parentReasonId=1000000425&orderCode=LP00135656817434&type=2&fromFlag=&outSystemRefId=',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = requests.get(url, headers=headers)
        print(self.cookie)
        print(response)
        print(response.text)

    def uploadImg(self):
        url = 'https://56newroute.oss-cn-shanghai.aliyuncs.com/'
        boundry = '---------------------------3899344131713'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Host": "crm-file.alibaba-inc.com",
            "Origin": "https://onetouch.alibaba.com",
            # "Content-Type":"multipart/form-data; boundary={}".format(boundry),
            "Pragma": "no-cache",
            # "Referer": "https://onetouch.alibaba.com/moSurvey/seller/detail.htm?tradeOrderId={}".format(self.order_id),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        }
        fr = open('shipping.png', 'rb').read()
        data = {
            'key': 'crm_cainiao/1563610369596-28Zw-shipping.png',
            'policy': 'eyJleHBpcmF0aW9uIjoiMjAxOS0wNy0yMFQwOToxMjo0OS41OTZaIiwiY29uZGl0aW9ucyI6W1siY29udGVudC1sZW5ndGgtcmFuZ2UiLDAsMTA0ODU3NjBdLFsic3RhcnRzLXdpdGgiLCIka2V5IiwiY3JtX2NhaW5pYW8vIl1dfQ==',
            'OSSAccessKeyId': 'nXOaB8BT48mO33gK',
            'success_action_status': 200,
            'signature': 'HkhfOJg3s88pTwZ+rJE2Xfbvcdg=',
            # 'big': True,
            # 'size': str(full_size),
            # 'type': t,
            # 'ownerApp': 'crmfile',
            # 'sceneCode': 'default_chunk',
            # 'mainCrmFileId': img_ali_name,
        }
        # fields = {
        #     'file': (img_name, fr, 'application/octet-stream')
        # }
        # response = requests.post(url, headers=fireFox_headers, files=fields, data=data, verify=False)

    def sendComlanit(self):
        url = 'https://workstation.i56.taobao.com/complainSelect.htm?type=2&orderId=135656817434'
        url = 'https://ilogistics.aliexpress.com/warehouse_order_list.htm'
        url = 'https://ilogistics.aliexpress.com/wlbComplain.htm?spm=5261.8869075.0.0.32943e5fp68YyI&orderId=142438435718&warehouseCarrierService=CAINIAO_STANDARD_TS_13171474'
        self.complaintImg = ComplaintImgSelenium(self.cookie, 'https://gsp.aliexpress.com/apps/order/index')
        self.complaintImg.browser.get(url)
        print(True)
        # self.complaintImg.browser.find_element_by_link_text('投诉').click()
        time.sleep(500)

    def main(self):
        self.getFaildOrder()
        # self.getCode()
        # self.getCookie2()
        # self.sendComlanit()


# 获取速卖通全部账号
def get_account():
    url = 'http://py2.jakcom.it:5000/aliexpress/get/account_cookie/all'
    response = requests.get(url)
    data = eval(response.text)
    return data['all_name']


def main():
    for account in get_account()[1:2]:
        # account = 'fb2@jakcom.com'
        print('**' * 50)
        print(account)
        print('**' * 50)
        shippingFaildOrder = ShippingFaildOrder(account)
        shippingFaildOrder.main()


if __name__ == '__main__':
    main()
