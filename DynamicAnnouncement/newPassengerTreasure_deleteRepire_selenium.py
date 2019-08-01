# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: newPassengerTreasure_deleteRepire_selenium.py.py
@time: 2019/5/17 14:36
@desc: 新客宝删除过期活动
"""
import time
from DynamicAnnouncement.public_selenium import Public_selenium


class NewPassengerTreasureDeleteRepire_selenium(Public_selenium):

    def __init__(self):
        super(NewPassengerTreasureDeleteRepire_selenium, self).__init__('https://work.1688.com/?spm=a262jn.11251430.workmenu.dseller_a.289c1768k6ObyP&_path_=sellerBaseNew/2017sellerbase_yingxiao/seller_activitymanager#/')

    # 删除过期活动, arg
    def index(self):
        # 获取所有活动
        activity_elements = self.browser.find_element_by_tag_name('tbody').find_elements_by_xpath('//tr')
        for index, activity_element in enumerate(activity_elements[1:]):
            # 遍历活动
            # 活动是否结束
            stautus = activity_element.find_elements_by_class_name('next-table-cell')[6].text
            # 活动名称
            name = activity_element.find_elements_by_class_name('next-table-cell')[1].text
            if stautus == '已结束':
                # 删除活动
                activity_element.find_element_by_link_text('删除').click()
                time.sleep(2)
                # 确认删除
                self.browser.find_element_by_xpath('//*[@id="dialog-footer-2"]/button[1]').click()
                # 发送日志
                self.send_test_log(logName='新客宝删除过期活动', logType='Run', msg='{} 删除成功'.format(name))
                # 刷新浏览器
                self.browser.refresh()
                # 返回True
                return True
        try:
            # 点击下一页
            self.browser.find_element_by_xpath('//*[@class="next-btn next-btn-normal next-btn-medium next-pagination-item next"]').click()
            # 继续删除结束活动
            self.index()
        except Exception as e:
            # 若发生错误，表示全部删除成功
            self.send_test_log(logName='新客宝删除过期活动', logType='Run', msg='删除完成')
            # 返回False
            return False


def delete():
    dele = NewPassengerTreasureDeleteRepire_selenium()
    while True:
        status = dele.index()
        # 如果status 时true，说明正在删除结束活动
        if status == True:
            # 存在已结束的活动
            status = dele.index()
        else:
            # 没有已结束的活动
            break


if __name__ == '__main__':
    delete()