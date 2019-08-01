# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: cookieSelenium.py
@time: 2019/6/20 19:08
@desc:
"""
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from shipping.IdentificationCodes import IdentificationCodes
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class CookieSelenium():

    # 类的初始化
    def __init__(self, url):
        """
        类的初始化
        """
        # 请求目标链接
        self.url = url
        # 构造浏览器对象
        self.browser = self.launch_web()
        self.action = ActionChains(self.browser)

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
        chrome_options.add_argument('--headless')
        # 加上这个属性来规避bug
        chrome_options.add_argument('disable-gpu')
        # 设置浏览器分辨率
        chrome_options.add_argument('window-size=1200,1100')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')
        # chrome_options.add_argument('referer=http://b2c.sf-express.com/ruserver/login/login.action')
        # chrome_options.add_argument('cookie=tgw_l7_route=aa957f0e7dac55e488ee256f5c2ebb4f; JSESSIONID=D16E788C9F0B73DB0FDC27ACB4FC9AA0.tomcat1.tomcat1')
        # 不加载图片
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 配置浏览器
        # chrome_options.add_experimental_option("prefs", prefs)
        # 启动浏览器
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.maximize_window()
        return browser

    def quit(self):
        self.browser.quit()

    def login_4PX(self):
        url = self.url
        self.browser.get(url)
        self.browser.find_element_by_id('loginName').send_keys('*****')
        self.browser.find_element_by_id('password').send_keys('*****')
        self.browser.find_element_by_id('loginBtn').send_keys(Keys.ENTER)
        cookies = self.browser.get_cookies()
        cookieJar = [i['name'] + '=' + i['value'] for i in cookies]
        return '; '.join(cookieJar)

    def login_PFC(self):
        url = self.url
        self.browser.get(url)
        self.browser.find_element_by_link_text('会员登录').click()
        self.browser.implicitly_wait(2)
        iframe = self.browser.find_element_by_id('layui-layer-iframe1')
        self.browser.switch_to_frame(iframe)
        self.browser.find_element_by_id('TxtUser').send_keys('*****')
        self.browser.find_element_by_id('Txtpassword').send_keys('*****')
        self.browser.find_element_by_id('Txtpassword').send_keys(Keys.ENTER)
        cookies = self.browser.get_cookies()
        cookieJar = [i['name'] + '=' + i['value'] for i in cookies]
        return '; '.join(cookieJar)

    def login_SF(self):
        url = self.url
        self.browser.get(url)
        self.browser.find_element_by_link_text('登录').click()
        time.sleep(0.5)
        self.browser.find_element_by_link_text('小包自助系统').click()
        self.browser.save_screenshot('get_image.png')
        element = self.browser.find_element_by_id('randomNum')
        left = element.location['x']
        top = element.location['y']
        right = element.location['x'] + element.size['width']
        bottom = element.location['y'] + element.size['height']
        im = Image.open('get_image.png')
        im = im.convert('RGB')
        im = im.crop((left, top, right, bottom))
        im.save('get_image.jpg')
        self.browser.find_element_by_id('loginname').send_keys('*****')
        self.browser.find_element_by_id('loginname').send_keys(Keys.F12)
        self.browser.find_element_by_id('mmPwd').send_keys('*****')
        identificationCodes = IdentificationCodes()
        code = identificationCodes.identification()
        self.browser.find_element_by_id('random1').send_keys(code)
        self.browser.find_element_by_id('mmPwd').send_keys(Keys.ENTER)
        time.sleep(0.5)
        now_url = self.browser.current_url
        print(now_url)
        if now_url != 'http://b2c.sf-express.com/ruserver/login/goMainFrame.action':
            return self.login_SF()
        else:
            cookies = self.browser.get_cookies()
            cookieJar = [i['name'] + '=' + i['value'] for i in cookies]
            return '; '.join(cookieJar)

    def main(self):
        self.login_SF()
        self.quit()

def main():
    url = 'http://b2c.sf-express.com/ruserver/login/login.action'
    cookieSelenium = CookieSelenium(url)
    cookieSelenium.main()

if __name__ == '__main__':
    main()
