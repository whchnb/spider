# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: alibabaFan_with_selenium.py
@time: 2019/5/10 17:23
@desc: 自动化完成每日文章发布
@upload time: 2019/5/16
@update content: 更新了卖点信息，优化了点击添加按钮后资源未加载的问题
"""
import time
import json
import random
import logging
import datetime
import requests
from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class CookieError(Exception):

    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorInfo = ErrorInfo

    def __str__(self):
        return self.errorInfo


class AlibabaFanSeleium():

    def __init__(self, account, SKU=None):
        """
        初始化对象
        :param account: 需要发布文章的账户
        :param SKU: 发布文章所需要对应的SKU
        """
        # 获取要发布信息的账户
        self.account = account
        # cookie 获取地址
        self.cookie_url = 'http://192.168.1.99:90/alibaba/get_cookie_byaccount?platform=Alibaba&account={}'.format(self.account)
        # 发布信息链接
        self.url = 'https://creator.alibaba.com/publish/post?spm=a2116r.creation-new-seller.main.1.365a138c8bbg57&from=feed&template=icbuVideo'
        # 创建14个feed 的索引列表，便于做到每日每个账户发布的文章类型不同
        self.feed_index_list = [i for i in range(1,15)]
        # 获得的SKU
        self.SKU = SKU
        # 初始化浏览器
        self.browser = self.launch_web()
        # 初始化鼠标
        self.action = ActionChains(self.browser)
        # 启动日志
        self.log()

    # 日志
    def log(self):
        """
        日志
        :return:
        """
        # 设置日志格式
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        # 添加日志时间
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
        # 设置日志内容
        logging.basicConfig(filename='fanPass.log',  # 日志名称及位置
                            level=logging.INFO,  # 设置日志级别
                            format=LOG_FORMAT,
                            datefmt=DATE_FORMAT)

    # 获取cookie
    def get_cookie(self):
        """
         获取cookie
        :return: 账户对应的cookie列表
        """
        print('正在获取cookie')
        response = requests.get(self.cookie_url)
        cookies = json.loads(response.text)
        cookie_list = cookies[0]['cookie_dict_list']
        return cookie_list

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
        # chrome_options.add_argument('window-size=1200,1100')
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
        cookie_list = self.get_cookie()
        for cookie in eval(cookie_list):
            # 将cookie添加到浏览器中
            browser.add_cookie({'name': cookie['name'], 'domain': cookie['domain'], 'value':cookie['value']})
        print('cookie 更改成功')
        # 重新打开链接
        browser.get(self.url)
        time.sleep(1)
        return browser

    # 添加视频
    def add_mp4(self):
        """
        添加视频
        """
        self.browser.implicitly_wait(30)
        print('点击添加视频')
        # 点击添加视频按钮
        self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[4]/div[1]/div[2]/form/div/div[3]/div/div[1]/div/div/div').click()
        # 获取视频
        status, self.mp4_id=self.get_mp4()
        # 视频id 以及视频名称
        self.video_id, self.mp4_name = self.get_mp4_id()
        time.sleep(2)
        print('点击添加封面图片')
        # 添加封面图片
        self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[2]/div[1]/div/div/div/div').click()
        time.sleep(1)
        print('选择图片分类')
        # 选择图片分类
        # self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[16]').click()
        # 选择活动主图图片分类
        for i in range(1, 19):
            # self.browser.delete_all_cookies()
            try:
                pic_class_element = self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[{}]'.format(i))
            except Exception as e:
                raise CookieError('添加主图时，cookie 出错,资源未加载，刷新页面重新开始')
            else:
                pic_class_name = pic_class_element.text
                if '活动主图' in pic_class_name:
                    self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[{}]'.format(i)).click()
                    print('切换活动主图成功')
                    break
        # 获取图片
        self.get_pic(1)
        time.sleep(1)
        print('视频及封面图片添加成功,点击确定')
        # 视频及封面图片添加成功后点击确定
        self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[3]/button[1]').click()

    # 获取视频
    def get_mp4(self, page=1):
        """
        获取视频
        :param page: 当前位于第几页
        :return (page, i): 若视频添加成功，返回True，如不存在，则继续添加视频, page 为当前页码数, i 为视频索引
        """
        for i in range(1,11):
            # 获取每个元素的视频名称
            try:
                mp4_element = self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[2]/div[1]/div[2]/div[{}]/div[2]/div[2]/div[1]/div/span/span'.format(i))
            except Exception as e:
                raise CookieError('获取视频时cookie 出错,资源未加载，刷新页面重新开始')
            else:
                mp4_name = mp4_element.text
                # 判断这个元素是否是需要添加的SKU 图片
                if self.SKU in mp4_name and 'Alibaba' not in mp4_name and 'alibaba' not in mp4_name:
                    # 点击图片选择添加
                    self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[2]/div[1]/div[2]/div[{}]/div[1]/div[1]'.format(i)).click()
                    print('视频添加成功，点击确定，正在添加封面图片')
                    # 点击添加封面按钮
                    self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[2]/div[2]/div/button[1]').click()
                    return True, (page, i)
        print('本页视频不存在，点击下一页')
        # 本页视频不存在，点击下一页按钮
        self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div[2]/div[1]/div[3]/div/div/button[2]').click()
        self.browser.implicitly_wait(30)
        # 继续添加
        page += 1
        return self.get_mp4(page=page)

    # 获取视频id
    def get_mp4_id(self):
        """
        获取视频id
        :return:  视频id
        """
        # 获取页数和索引
        page, index = self.mp4_id
        # 获取视频id 的链接
        url = 'https://message.alibaba.com/message/content/material/pageVideo.htm?type=video&current={}'.format(page)
        response = requests.get(url, headers=self.headers)
        data = json.loads(response.text)['data']['itemList'][index - 1]
        # 视频id
        id = data['videoId']
        # 视频链接
        mp4_url = data['playUrl']
        # 视频名称
        mp4_name = data['title']
        # 返回视频名称
        return id, mp4_name
        # print(id, mp4_name, mp4_url)

    # 添加图片
    def add_pic(self):
        """
        添加图片
        """
        time.sleep(2)
        print('点击添加主图片')
        # 添加图片
        self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[4]/div[1]/div[2]/form/div/div[4]/div/div[1]/div/div').click()
        self.browser.implicitly_wait(30)
        time.sleep(2)
        print('点击主图片分类')
        # 选择活动主图图片分类
        for i in range(1, 19):
            try:
                pic_class_name = self.browser.find_element_by_xpath('//*[@id="dialog-body-4"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[{}]'.format(i)).text
            except Exception as e:
                raise CookieError('添加主图片时，cookie 出错，资源未加载')
            else:
                if '活动主图' in pic_class_name:
                    self.browser.find_element_by_xpath('//*[@id="dialog-body-4"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[{}]'.format(i)).click()
                    break
        # self.browser.find_element_by_xpath('//*[@id="dialog-body-4"]/div/div/div/div[2]/div/div/div[1]/ul/li/ul/li[16]').click()
        time.sleep(2)
        self.browser.implicitly_wait(30)
        # sku_list = self.browser.find_elements_by_class_name('/div[@class="ice-any-picker__trigger"]')
        # 获取图片
        self.get_pic(4)
        # 翻页操作
        self.browser.find_element_by_css_selector('body').send_keys(Keys.PAGE_DOWN)

    # 添加产品
    def add_products(self):
        """
        添加产品
        :return:
        """
        self.browser.implicitly_wait(30)
        time.sleep(0.5)
        print('点击添加产品')
        # 点击添加产品按钮
        self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[4]/div[1]/div[2]/form/div/div[5]/div/div[1]/div/div').click()
        self.browser.implicitly_wait(30)
        print('选择产品分类')
        # 重新获取所有sku
        skus = self.get_sku()
        # 移除正在使用的SKU，确保添加的产品中不存在此SKU
        skus.remove(self.SKU)
        for i in range(9):
            # 随机选择任意一个sku，并将它从skus 列表中移除
            sku = skus.pop(random.choice(range(len(skus))))
            # sku = 'CS2'
            # sku = 'BH3'
            if sku == 'BH3':
                # 如果sku 为'BH3'，则选择Smart Bluetooth Headphones 分组
                self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[1]/ul/li[7]').click()
            elif sku == 'H1':
                # 如果sku 为'H1'，则选择Smart Watch 分组
                self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[1]/ul/li[4]').click()
            else:
                # 选择Hot Sale分组
                self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[1]/ul/li[11]').click()
            self.browser.implicitly_wait(30)
            print('选择添加的SKU型号为', sku)
            print('点击搜索框')
            # 选择搜索框
            self.action.click(self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/span/div/div/input'))
            # time.sleep(2)
            self.browser.implicitly_wait(30)
            print('添加搜索关键字')
            # 添加需要搜索的sku
            self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/span/div/div/input').send_keys(sku)
            print('确认搜索')
            self.browser.implicitly_wait(30)
            time.sleep(1)
            # 确认搜索
            self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/span/div/div/input').send_keys(Keys.ENTER)
            self.browser.implicitly_wait(30)
            time.sleep(1)
            print('点击添加产品')
            for i in range(1, 5):
                print('当前判断第{}个产品'.format(i))
                product_element = self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[2]/div[{}]/div[1]'.format(i))
                product_name = self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[2]/div[{}]/div[2]/a'.format(i)).text
                print('产品名称', product_name)
                # 判断添加的产品名称中不含敏感词
                if 'Alibaba' not in product_name and 'alibaba' not in product_name:
                    print(True)
                    try:
                        # 点击添加产品
                        product_element.click()
                    except:
                        # 若发生错误，等待3秒，重新添加
                        print('点击速度太快')
                        time.sleep(3)
                        try:
                            product_element.click()
                        except Exception as e:
                            msg = '{} {}'.format(self.account, str(e))
                            self.send_log('Error', msg, position='Error in function add_products')
                    finally:
                        break
                else:
                    print(False)
                    continue

            self.browser.implicitly_wait(30)
            # time.sleep(1)
            print('全选搜索框文字')
            # 全选搜索框中的sku
            self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/span/div/div/input').send_keys(Keys.CONTROL + 'a')
            print('删除搜索文字')
            self.browser.implicitly_wait(30)
            # 删除已经添加完成的sku
            self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/span/div/div/input').send_keys(Keys.DELETE)
            # time.sleep(2)
        print('产品添加成功，点击确定')
        # 添加完成后，点击确定按钮
        self.browser.find_element_by_xpath('//*[@id="dialog-footer-2"]/div/div[2]/button[1]').click()
        time.sleep(2)

    # 获取图片
    def get_pic(self, class_):
        """
        获取图片
        :param class_: 获取图片的类型， 1为视频图片，4为封面图片
        :return: 添加成功，返回True，否则选择下一页继续添加
        """
        print('class is ', class_)
        for i in range(1, 21):
            # 获取每个元素的名称
            html_sku = self.browser.find_element_by_xpath('//*[@id="dialog-body-{}"]/div/div/div/div[2]/div/div/div[2]/div[2]/div[{}]/div[2]/div[2]'.format(class_, i)).text
            # 判断元素的名称是否是需要添加的SKU
            if self.SKU in html_sku:
                print('点击选择封面图片')
                # 选择封面图片
                self.browser.find_element_by_xpath('//*[@id="dialog-body-{}"]/div/div/div/div[2]/div/div/div[2]/div[2]/div[{}]/div[1]'.format(class_,i)).click()
                self.browser.implicitly_wait(30)
                print('点击确定添加图片')
                if class_ == 1:
                    time.sleep(0.5)
                    # 添加图片完成后点击确定按钮
                    self.browser.find_element_by_xpath( '//*[@id="dialog-footer-2"]/div/div[2]/button[1]').click()
                else:
                    self.browser.find_element_by_xpath('//*[@id="dialog-footer-{}"]/div/div[2]/button[1]'.format(class_ + 1)).click()
                return True
        time.sleep(0.5)
        print('当前页面不存在，点击下一页')
        # 点击下一页按钮
        self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-normal next-btn-small next-pagination-item next"]').click()
        time.sleep(2)
        # 继续获取图片
        return self.get_pic(class_)

    # 获取feed
    def get_feed(self):
        """
        获取文章feed 类型
        :return: feed 类型
        """
        # time.sleep(10)
        # 将页面滑动到最后
        self.browser.find_element_by_css_selector('body').send_keys(Keys.END)
        # 选择随机feed 的名称索引
        feed_index = self.feed_index_list.pop(self.feed_index_list.index(random.choice(self.feed_index_list)))
        # print(feed_index)
        time.sleep(1)
        print('点击需要feed的类型框')
        # 点击需要feed的类型框
        self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[4]/div[1]/div[2]/form/div/div[6]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[{}]/label/span[1]/input'.format(feed_index)).click()
        time.sleep(1)
        print('获取feed 的文字')
        # 获取feed 的文字
        class_name = self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[4]/div[1]/div[2]/form/div/div[6]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[{}]/label'.format(feed_index)).text
        # 返回获取feed 的文字
        return class_name

    # 获取标题和卖点
    def get_title_sellPoint(self, class_name):
        """
        获取标题和卖点
        :param class_name: 卖点
        """
        # feed 类型
        self.feedType = class_name
        # 构造文章的title
        self.title = '{}-{}-{}'.format(self.SKU, class_name, str(datetime.datetime.now().date()).replace("-", ""))
        # 构造卖点
        sellingPoint = "Products, accessories, packaging,  All-round free customization;\nArrange shipping within 24 hours;\nNo increase in price.\nNo MOQ limit.."
        print('添加标题')
        # 添加标题
        self.browser.find_element_by_xpath('//*[@id="title"]').send_keys(self.title)
        print('添加卖点')
        # 添加卖点
        self.browser.find_element_by_xpath('//*[@id="summary"]').send_keys(sellingPoint)

    # 点击发布
    def submit(self):
        """
        发布文章
        """
        # 保存草稿按钮
        # self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[3]/div/div[2]/button[1]').click()
        # 视频发布按钮
        submit = self.browser.find_element_by_xpath('//*[@id="ice_container"]/div/div/div[2]/div/div/div[3]/div/div[2]/div/button')
        print(submit.text)
        self.browser.implicitly_wait(30)
        time.sleep(1)
        if submit.text == '发布(今日还可发布：0篇)':
            msg = '{} 已达今日发布上限'.format(self.account)
            self.send_log('Run', msg)
            self.browser.close()
            # del alibaba
        else:
            submit.click()
            time.sleep(3)
            try:
                # 判断此视频是否已经使用，若使用则点击继续发布，若位使用，抛出异常
                self.browser.find_element_by_xpath('//*[@class="next-dialog right next-overlay-inner animated fadeInDown confirm-dialog next-position-cc"]')
                # self.browser.find_element_by_xpath('//*[@id="dialog-footer-2"]/div/button[1]')
                self.browser.find_element_by_xpath('//*[@id="dialog-footer-2"]/div/button[2]').click()
                self.browser.implicitly_wait(30)
                time.sleep(5)
            except Exception as e:
                print(e)
            finally:
                if  'creator.alibaba.com/publish/post' in str(self.browser.current_url).split('?')[0]:
                    message = ''
                    try:
                        message = self.browser.find_element_by_xpath('//*[@id="dialog-body-1"]').text
                    except Exception as e:
                        print(e)
                    finally:
                        msg = '{} 发布失败 {} {}'.format(self.account, self.browser.current_url, message)
                        self.send_log('Error', msg)
                else:
                    msg = '{} 发布正常'.format(self.account)
                    self.send_log('Run', msg)
                    self.send_fanPass_log(msg)

    # 改变页面
    def change_index(self):
        """
        改变页面
        """
        # 打开链接
        self.browser.get(self.url)
        try:
            # 离开页面后会出现弹窗提示
            alert = self.browser.switch_to_alert()
            # 选择确定离开页面
            alert.accept()
        except:
            pass

   # 获取sku
    def get_sku(self, use=None):
        """
        获取SKU
        :return: sku列表
        """
        # 获取sku的链接
        url = "http://192.168.1.99:90/alibaba/skulist"
        response = requests.get(url).text
        sku_list = json.loads(response)
        if use == 'all':
            # 获取用户当天已经发布过的SKU
            released_sku_list = self.get_released_skus()
            print('{} 当天已发布的SKU有: {}'.format(self.account, ','.join(released_sku_list)))
            # 从SKU 列表中移除已发布的sku
            for sku in released_sku_list:
                sku_list.remove(sku)
        # 返回sku 列表
        return sku_list

    # 获取用户当天已经发布过的SKU
    def get_released_skus(self):
        """
        获取用户当天已经发布过的SKU
        :return: 已经发布过的SKU_list
        """
        # 构建搜索时间
        date = datetime.datetime.now().date()
        url = 'https://creator.alibaba.com/merchant/list.json?__version__=3.0&tab=all&subTab=all&range={}...{}&titleSearch='.format(date, date)
        # 获取cookie_list
        cookie = self.get_cookie()
        # 初始化cookie
        custom_cookie = ''
        for i in eval(cookie):
            # 拼接cookie
            custom_cookie = custom_cookie + i['name'] + '={}; '.format(i['value'])
        self.headers = {
            'authority': 'creator.alibaba.com',
            'method': 'GET',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': custom_cookie,
            'referer': 'https://creator.alibaba.com/creation/all?tab=all&subTab=all',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = requests.get(url, headers=self.headers)
        # 加载数据
        datas = json.loads(response.text)['data']['components'][3]['props']['dataSource']
        released_sku_list = []
        # 便利数据
        for data in datas:
            # 获取当天已经发布过的SKU
            sku_name = data['title']['title'].split('-')[0]
            # 添加到released_sku_list
            released_sku_list.append(sku_name)
        # 将sku 去重后返回
        return list(set(released_sku_list))

    # 发送日志
    def send_log(self, logType, msg, position='0'):
        msg = str(msg)
        test_url = 'http://192.168.1.99:90/Log/Write'
        data = {
            'LogName': '粉丝通',
            'LogType': logType,
            'Position': position,
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': msg,
        }
        test_response = requests.post(test_url, data=data)
        print('test_response',test_response.text)
        logging.info('{} 发送测试日志 {} {}'.format(self.account, msg, test_response.text))

    # 粉丝通日志
    def send_fanPass_log(self, msg):
        fanPass_log_url = 'http://192.168.1.99:90/alibaba/Log_feed_promotion'
        data = {
            'Account': self.account,
            'FeedVideo': self.mp4_name,
            'VideoID': self.mp4_id,
            'FeedType': self.feedType,
            'FeedTitle': self.title,
            'SKU': self.SKU,
            'Createtime': str(datetime.datetime.now())
        }
        fanPass_log_response = requests.post(url=fanPass_log_url, data=data)
        print('fanPass_log_response', fanPass_log_response)
        logging.info('{} 发送粉丝通日志 {} {} {}'.format(self.account, data, msg, fanPass_log_response.text))


if __name__ == '__main__':
    start_time = time.time()
    cookie_accounts = [
        # "fb1@jakcom.com",
        # "fb2@jakcom.com",
        "fb3@jakcom.com",
        "tx@jakcom.com",
    ]
    for account in cookie_accounts:
        print('当前用户: {}'.format(account))
        alibaba = AlibabaFanSeleium(account)
        # 获得全部SKU
        SKUS = alibaba.get_sku(use='all')
        print(SKUS)
        alibaba.get_released_skus()
        for i in range(1, 15):
            print('+*-'*20)
            print('正在发布第{}条'.format(i))
            # 随机选择一个SKU， 并将他从列表中移除
            SKU = SKUS.pop(random.choice(range(len(SKUS))))
            print(SKU)
            try:
                alibaba.SKU = SKU
                # 添加视频
                alibaba.add_mp4()
                # 添加图片
                alibaba.add_pic()
                # 添加商品
                alibaba.add_products()
                # 获取feed 类型
                class_name = alibaba.get_feed()
                # 添加标题和卖点信息
                alibaba.get_title_sellPoint(class_name)
                # 提交发布
                alibaba.submit()
                alibaba.change_index()
            except CookieError as c:
                alibaba.send_log('Error', c)
                print('cookie 出错，资源未加载，30秒后继续添加')
                SKUS.append(SKU)
                time.sleep(30)
                continue
            except UnboundLocalError as u:
                break
            except Exception as e:
                print(e)
                alibaba.send_log('Error', e)
                print('发布第{}条时发生错误'.format(i))
                print('正在切换页面')
                SKUS.append(SKU)
                # 若发生错误则切换至首页，便于下一条内容的发布
                alibaba.change_index()
        del alibaba
        end_time = time.time()
        print('{}发布文章所用时间{}'.format(account, end_time - start_time))