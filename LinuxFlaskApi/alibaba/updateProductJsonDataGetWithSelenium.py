# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: updateProductJsonDataGetWithSelenium.py
@time: 2019/7/29 9:00
@desc: alibaba 在线产品修改类目模板数据获取
"""
import time
import requests
from selenium import webdriver
from alibaba.public import Public
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class UpdateProductJsonDataGetWithSelenium(Public):
    def __init__(self, account):
        self.account =account
        super(UpdateProductJsonDataGetWithSelenium, self).__init__(self.account)
        self.browser = self.launch_web()

    # 浏览器配置
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
        # 设置代理
        chrome_options.add_argument("--proxy-server=http://proxy.jakcom.it:1688")
        # 加上这个属性来规避bug
        chrome_options.add_argument('disable-gpu')
        # 设置浏览器分辨率
        chrome_options.add_argument('window-size=1200,1100')
        # 不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }
        # 配置浏览器
        chrome_options.add_experimental_option("prefs", prefs)
        # 配置浏览器日志
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = {'performance': 'ALL'}
        # 启动浏览器
        browser = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=d)
        browser.maximize_window()
        # 使用浏览器打开链接
        browser.get('https://hz-productposting.alibaba.com/product/products_manage.htm')
        # 删除浏览器生成的cookie
        browser.delete_all_cookies()
        # 获取账户对应cookie
        cookie_list = self.get_selenium_cookie()
        # cookie_list = [{'name': 'UM_distinctid', 'value': '16a8b52b22d7d-059d3153703b06-e323069-1fa400-16a8b52b22e3a3', 'domain': '.1688.com'}, {'name': 'cna', 'value': 'n4lWFZbRW2YCAbe/sh4Lxj33', 'domain': '.1688.com'}, {'name': 'ali_apache_id', 'value': '11.186.201.38.1557135135792.051504.0', 'domain': '.1688.com'}, {'name': 'lid', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': 'ali_apache_track', 'value': 'c_mid', 'domain': '.1688.com'}, {'name': '_umdata', 'value': 'G282AA9260EB76ED2F44C5C50B4F02B62A8CB81', 'domain': '.1688.com'}, {'name': '__utma', 'value': '62251820.53433343.1557966739.1557966739.1557966739.1', 'domain': '.1688.com'}, {'name': '__utmz', 'value': '62251820.1557966739.1.1.utmcsr', 'domain': '.1688.com'}, {'name': 'ali_ab', 'value': '183.191.179.144.1557982246155.1', 'domain': '.1688.com'}, {'name': 'h_keys', 'value': '"airpods#%u7b14%u8bb0%u672c%u7535%u8111#%u4eca%u65e5%u7279%u4ef7%u4ea7%u54c1%u63a8%u8350"', 'domain': '.1688.com'}, {'name': 'ad_prefer', 'value': '"2019/05/17 17:14:07"', 'domain': '.1688.com'}, {'name': 'XSRF-TOKEN', 'value': '439222b9-203c-4eec-ace0-e80df19f2574', 'domain': '.1688.com'}, {'name': 'cookie2', 'value': '19b7fc93fef75fa8606d3a6e445f6a09', 'domain': '.1688.com'}, {'name': 't', 'value': '1f71f19a13a626847bf3376cbfa1cbe0', 'domain': '.1688.com'}, {'name': '_tb_token_', 'value': 'ef3733b6e9097', 'domain': '.1688.com'}, {'name': '__cn_logon__', 'value': 'true', 'domain': '.1688.com'}, {'name': '__cn_logon_id__', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': 'ali_apache_tracktmp', 'value': 'c_w_signed', 'domain': '.1688.com'}, {'name': 'last_mid', 'value': 'b2b-2257499635', 'domain': '.1688.com'}, {'name': 'ctoken', 'value': 'kyN0MeiOkXxS5dO88Gvrcoco', 'domain': '.1688.com'}, {'name': 'cookie1', 'value': 'BxoD8yON%2BLKP2nR%2FU%2BsuODsyQQ7FVtqL2homXzhyRFg%3D', 'domain': '.1688.com'}, {'name': 'cookie17', 'value': 'UUpkv67HfD0F4g%3D%3D', 'domain': '.1688.com'}, {'name': 'sg', 'value': 'm53', 'domain': '.1688.com'}, {'name': 'csg', 'value': '82d796ca', 'domain': '.1688.com'}, {'name': 'unb', 'value': '2257499635', 'domain': '.1688.com'}, {'name': '_nk_', 'value': 'jakcomcom', 'domain': '.1688.com'}, {'name': '_csrf_token', 'value': '1558519010993', 'domain': '.1688.com'}, {'name': '_is_show_loginId_change_block_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_force_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_sys_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '_show_user_unbind_div_', 'value': 'b2b-2257499635_false', 'domain': '.1688.com'}, {'name': '__rn_alert__', 'value': 'false', 'domain': '.1688.com'}, {'name': 'alicnweb', 'value': 'touch_tb_at%3D1558519020097%7Clastlogonid%3Djakcomcom%7Cshow_inter_tips%3Dfalse', 'domain': '.1688.com'}, {'name': 'l', 'value': 'bBM41yPPvD94RXr2KOfwSuI8LS7tEIRbzsPzw4OgiICP_IWM5M_PWZtWS9xHC3GVa6nDJ3kM34SXBcY7ryznh', 'domain': '.1688.com'}, {'name': 'isg', 'value': 'BEJCISftqvg2lbaOQ7ogMIulk0hku0etnt4f34xbqLVg3-BZdafCPFldi5sGj77F', 'domain': '.1688.com'}]
        for cookie in (cookie_list):
            # 将cookie添加到浏览器中
            browser.add_cookie({'name': cookie.strip().split('=')[0], 'domain': '.alibaba.com', 'value':cookie.strip().split('=')[1]})
        print('cookie 更改成功')
        # 重新打开链接
        browser.get('https://hz-productposting.alibaba.com/product/products_manage.htm')
        return browser

    # 获取cookie
    def get_selenium_cookie(self):
        return self.cookie.split(';')

    # 退出浏览器
    def quit(self):
        self.browser.quit()

    # 检测模板表单数据是否获取成功
    def checkProductJsonData(self, itemId):
        url = "http://py1.jakcom.it:5000/alibaba/post/info/item_post_data"
        data = {
            "item_id": itemId
        }
        response = requests.post(url, data=data)
        if len(response.text) > 10:
            return True
        return False

    # 获取类目 sku 的表单模板
    def getItemId(self):
        url = 'http://cs1.jakcom.it/alibabaproductmanage/group_product_bycate_sku?account=' + self.account
        response = requests.get(url)
        itemIdList = [i['ProductId'] for i in response.json()]
        return itemIdList

    def logSaveAsLocal(self, itemId):
        file = open('/run/user/1000/gvfs/smb-share:server=192.168.1.98,share=公共共享盘/@ Code/Log/Alibaba/%s_%s_Post_Data.log' % (self.account.split('@')[0], itemId), 'w')


    def main(self):
        itemIdList = self.getItemId()
        for index, itemId in enumerate(itemIdList):
            print('**' * 50)
            print(index, itemId)
            print('**' * 50)
            url = 'https://post.alibaba.com/product/publish.htm?itemId=' + itemId
            self.browser.get(url)
            try:
                # 如果不是第一次获取, 确定弹窗
                if index != 0:
                    alert = Alert(self.browser)
                    alert.accept()
                url = 'https://post.alibaba.com/product/publish.htm?itemId=' + itemId
                self.browser.get(url)
                self.browser.find_element_by_tag_name('body').send_keys(Keys.ENTER)
                # time.sleep(index * 5000)
                for i in range(9):
                    self.browser.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
                self.browser.find_element_by_xpath('//*[@id="struct-buttons"]/button[4]').click()
                time.sleep(3)
                productDataStatus = self.checkProductJsonData(itemId)
                print(productDataStatus)
                if productDataStatus is False:
                    self.send_test_log(logName='alibaba产品更新数据获取', logType='Error', msg='%s %s' % (self.account, itemId))
            except Exception as e:
                self.logSaveAsLocal(itemId)
                self.send_test_log(logName='alibaba产品更新数据获取', logType='Error', msg='%s %s %s' % (self.account, itemId, str(e)))
                continue

def bug(msg, position='0'):
    msg = str(msg)
    test_url = 'http://192.168.1.160:90/Log/Write'
    data = {
        'LogName': 'alibaba产品更新数据获取',
        'LogType': 'Running Failed',
        'Position': position,
        'CodeType': 'Python',
        'Author': '李文浩',
        'msg': msg,
    }
    test_response = requests.post(test_url, data=data)
    print('test_response', test_response.text)



def main():
    accountList = [
        'tx@jakcom.com',
        'fb2@jakcom.com',
        'fb3@jakcom.com',
    ]
    for account in accountList:
        # account = 'tx@jakcom.com'
        try:
            updateProductJsonDataGetWithSelenium = UpdateProductJsonDataGetWithSelenium(account)
            updateProductJsonDataGetWithSelenium.main()
            updateProductJsonDataGetWithSelenium.quit()
            return True
        except Exception as e:
            print(e)
            bug(msg='%s %s' % (account, str(e)))
            return e


if __name__ == '__main__':
    main()