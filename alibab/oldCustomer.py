# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: oldCustomer.py
@time: 2019/5/25 15:32
@desc:
"""
import re
import csv
import sys
import time
import json
import requests
from alibaba.public import Public


class Customer(Public):

    # 继承父类__init__ 方法
    def __init__(self, account):
        self.account = account
        self.count = 0
        super(Customer, self).__init__(self.account)

    # 获取所有国家
    def get_all_country(self):
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/dictionaryQueryServiceI/queryDicList.json'
        params = {
            'type': 'NATIONAL_AREA',
            '_tb_token_': self.tb_token,
            '__t__': str(time.time()).replace('.', '')[:13]
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = json.loads(response.text)['data']['data']
        return datas

    # 运行主函数
    def main(self, country, page, url_link):
        country_code = country['code']
        url = url_link.format(self.tb_token)
        post_data = {
            'jsonArray':  '[{"id":"664","country_code":"%s"}]'%country_code,
            'orderDescs': [{ 'asc': False,'col': 'opp_gmt_modified'}],
            'pageNum': page,
            'pageSize': 500    # 500
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(post_data))
        # 获取全部的数据
        datas = json.loads(response.text)['data']['data']
        # 获取各个国家的客户信息数量
        total = json.loads(response.text)['data']['total']
        print('当前国家{} 共有客户{}个'.format(country_code, total))
        # 当页共有客户数据个数
        numbers = len(datas)
        if numbers != 0:
            # 获取蓝标客户字典
            blueTag_dict = {
                'A': '蓝标客户'
            }
            # 用户分组字典
            customerGroup_dict = {
                'NA': '未分组',
                '2': '成交客户',
                '1': '样单客户',
                '0': '询盘客户',
            }
            # 商业类型字典
            businessTypes_dict = {
                '2001': '工厂',
                '2002': '贸易公司',
                '2003': '批发/分销商',
                '2004': '线下零售商',
                '2005': '采办/采购代理',
                '2006': '线上零售商',
                '2007': '散客',
                '2008': '其他',
            }
            # 客户来源字典
            customerSources_dict = {
                'Ta': '订单',
                'Onestop': '电商一站式服务'

            }
            # 流失预警字典
            willLoss_dict = {
                'y': '流失预警',
                'n': '高潜复购',
                '非公海客户无流失预警': '非公海客户无流失预警'
            }
            # 商品类型字典
            shops_id_name = {'301001': '锁具零件', '3014': '警卫服务', '301002': '钥匙', '708045': '主板', '301003': '锁匠工具', '3016': '其它安防产品', '708044': '显卡', '708041': '散热系统', '708042': '中央处理器', '100007346': '表盒', '100007347': '拳击球', '100007324': '首饰套装', '100010905': '摄影工作室用品', '100010906': '游戏机支架', '100007323': '戒指', '100010903': '镜头转接环', '100010904': '微型摄像机', '100010901': '相机电池手柄', '100007320': '项链', '100000663': '指甲贴', '5092399': '其它广播&电视附件', '100010916': '电源适配器', '100010912': '耳机配件', '100010909': '便携式收音机', '100010910': '电子阅读器', '127666033': '其他大灯', '303099': '其他门禁产品', '127688045': '智能手环', '100010899': '摄影灯', '100010900': '快门线和遥控器', '100010897': '相机带', '100010898': '柔光罩', '12020305': '汽车喇叭', '100010895': '移动电源', '100010896': '稳定器', '7171': 'USB新奇特', '100010893': '数据线', '7172': '硬盘盒', '100010894': '绕线器', '70803005': '数据交换机', '518': '扬声器', '100000636': '指甲胶水', '5092302': '卫星电视接收器', '523': '传感器', '100000631': '水晶粉', '5092303': '机顶盒', '70803001': '路由器', '70803002': '网络集线器', '70803003': '电脑分享器', '70803004': '网卡', '12020399': '其它汽车电子电器', '7080401': '液晶显示器', '100000603': '沐浴珠', '330801': '人工指甲', '2107': '投影仪', '330808': '指甲烘干机', '2118': '打印机', '127820001': '遥控器', '127820002': '手机', '100009284': '相机闪光灯', '5093004': '手机座', '601': '家用空调', '604': '家用DVD, VCD 播放机', '613': '空气净化器', '100009249': '手写笔', '628': '其它家用电器', '632': '家用收音机', '634': '电视机', '5091005': '电话听筒、耳机', '635': '家庭影院系统', '127756006': '其它显示器', '100001017': '低音喇叭', '100001013': '车载收音机', '100001016': '车载功放', '70802': '键盘', '70803': '调制解调器', '70805': '鼠标', '127818001': '视频眼镜', '70807': '其它存储设备', '361120': '怀表', '2212': '音乐', '5904003': '手机机壳', '5904002': '手机显示屏幕', '1716': '金属工艺品', '127690031': '其他智能家居', '127734058': '扬声器配件', '701': '台式电脑及一体机', '702': '笔记本电脑', '127734060': '智能遥控器', '704': 'PDA', '705': '其它网络设备', '1730': '库存礼品，工艺品', '707': '其它电脑部件', '1735': '礼品套装', '1737': '音乐盒', '717': '其它电脑产品', '720': '机箱', '721': '笔记本散热器', '100006078': '擂台', '5092102': '电视天线', '100006077': '沙包', '100006079': '其它拳击器材', '5092103': '手机天线', '63701': '扩音器', '201153201': '智能安防设备', '63703': '便携式CD播放机', '63704': '数码录音笔', '63705': '耳塞和耳机', '63707': '卡拉OK播放机', '63708': '麦克风', '63710': 'MP3 播放器', '100000433': '充电器', '127678021': 'LED头灯', '100000432': '电池', '370399': '其它家用家具', '70899': '其它电脑附件', '70901': '电脑电源', '190000172': '智能手表', '100010614': '平板电脑', '5090502': '无线广播&电视广播设备', '127654030': '其他汽车配件', '127654029': '其他雾/驾驶灯', '18060304': '游戏光枪', '14190408': '电力电缆', '100000346': '其它零配件', '127694020': '其他的尾灯', '100000344': '电视机支架', '127652033': '灯泡', '380210': '照相机,摄像机包/袋', '5093099': '其他手机配件', '4402': '硬盘播放机', '4403': '古兰经播放器', '4406': '储存卡', '127822001': 'U盘', '63799': '其他家庭音视频设备', '4407': '读卡器', '4408': '屏幕保护膜', '4409': '数码产品清洁用品', '100006482': '车载蓝牙免持听筒套件', '100000335': '蓝光播放机', '380230': '手机包', '380250': 'PDA包', '100002860': '腕表工具和和部件', '711006': '刻录盘', '100002859': '表带', '100001830': '其它节日用品', '190303': '相机滤镜', '190301': '摄影背景', '127684037': '智能手表', '190307': '三脚架', '711004': '光驱', '100002861': '腕表', '711001': '硬盘', '190305': '相机镜头', '711002': '内存', '14190401': '音频/视频线', '1901': '胶片相机', '1902': '摄像机', '100001825': '圣诞装饰', '1908': '胶卷', '1909': '数码相机', '18060399': '其它游戏附件', '100005395': '步程计', '100001788': '贴纸', '120201': '汽车电池', '4499': '其它消费电子产品', '100001791': '其它户外运动玩具', '201148402': '遥控交通工具玩具', '303002': '门禁系统', '303003': '商品电子防盗系统', '100003314': '车载电源转换器', '127660038': '智能配件', '303006': '门禁卡', '303007': '门禁读卡器', '303008': '语音电话', '39050101': '手电筒', '100005845': '其它健身及塑形产品', '708031': '贴纸、皮肤', '100005324': '软驱', '100005330': '工控产品', '708023': '鼠标垫 & 衬垫', '190399': '其它相机附件', '7101': '扫描仪', '100005329': '切换器', '708024': '键盘鼠标套装', '708021': '键盘保护膜', '3008': '警报器', '100005326': '防火墙和VPN', '100005325': '触摸屏显示器', '3010': '锁具', '100005328': '网络机柜', '100005327': '网络存储', '3012': '保险柜'}
            for index, data in enumerate(datas):
                print('当前国家{} 当前页数{} 共{}条 正在获取第{}条'.format(country_code, page, numbers, index))
                try:
                    saleName = data.get('saleName', '公海客户无业务员')                                    # 业务员          Ady JAKCOM
                    originSaleName = data['originSaleName'] if data['originSaleName'] is not None else '非公海客户无原业务员'            # 原业务员
                    potentialScore = data.get('potentialScore', '非公海客户无潜力分')                # 潜力分
                    customerId = data['customerId']                         # md5 id          3ea91e636c6c565739ce8f69d1ee218f
                    companyName = data['companyName']                       # 公司名称
                    aliId = data['mainContact']['aliId']                    # 阿里id          133493792210
                    loginId = data['mainContact']['loginId']                # 登录id          sa1340044731celt
                    buyerID = data['mainContact']['contactName']            # 客户姓名
                    wangwangID = data['mainContact']['wangwangId']          # 旺旺id          8pctgRBMALMfLIST8sj/GVkt8XivkCB66wdkfYSa+s4=
                    referenceId = data['mainContact']['referenceId']        # 参考id          958407859
                    blueTag = data['mainContact']['blueTag']
                    blueTag = blueTag_dict.get(blueTag, blueTag)            # 蓝标            c
                    customerGroup = customerGroup_dict[data['customerGroup']]                # 客户分组     customerGroup_list
                    importanceLevel = data['importanceLevel']               # 重要星级      0 未设置       1 1星    2 2星    3 3星
                    groupName = '未设置分群' if data['marketingGroups'] is None else data['marketingGroups'][0]['groupName']       # 客户分群
                    businessTypes = data['businessTypes']
                    businessType = ','.join([businessTypes_dict[i] for i in businessTypes]) if len(businessTypes) != 0 else '未设置商业类型'   # 商业类型      businessTypes_dict
                    countryCode = data['countryCode']                       # 国家地区
                    categorys = data['categorys']
                    category = ','.join([shops_id_name.get(category, '-') for category in categorys]).replace('-,', '') if len(categorys) != 0 else '无采购品类'     # 采购品类      shops_id_name
                    customerSources = data['customerSources']
                    customerSource = ','.join([customerSources_dict.get(i, i) for i in customerSources]) if len(customerSources) != 0 else '客户来源未知'     # 客户来源      customerSources_dict
                    createDate = data['createDate']                         # 建档时间
                    noteTime = data['recentNote']['noteTime'] if data['recentNote'] is not None else None       # 小计时间
                    noteContent = data['recentNote']['content'] if data['recentNote'] is not None else None     # 跟进小记
                    willLoss = willLoss_dict[data.get('willLoss', '非公海客户无流失预警')]              # 流失预警
                    isDing = data.get('isDing', '非公海客户无钉住状态')                                 # 钉住状态
                    # 用户数据
                    costomer_data = {
                        'saleName': saleName,
                        'originSaleName': originSaleName,
                        'potentialScore': potentialScore,
                        'customerId': customerId,
                        'companyName': companyName,
                        'aliId': aliId,
                        'loginId': loginId,
                        'buyerID': buyerID,
                        'wangwangID': wangwangID,
                        'referenceId': referenceId,
                        'blueTag': blueTag,
                        'customerGroup': customerGroup,
                        'importanceLevel': importanceLevel,
                        'groupName': groupName,
                        'businessType': businessType,
                        'countryCode': countryCode,
                        'category': category,
                        'customerSource': customerSource,
                        'createDate': createDate,
                        'noteTime': noteTime,
                        'noteContent': noteContent,
                        'willLoss': willLoss,
                        'isDing': isDing,
                    }
                    # 获取在线聊天内容
                    chat_detail = self.chat_online(customerId)
                    # 获取询盘信息
                    inquiry_detail = self.inquiry(customerId)
                    # 获取订单跟踪信息
                    order_tracking_detail = self.order_tracking(customerId)
                    # 获取客户详细信息
                    info_number_detail = self.get_info_detail(customerId, referenceId)
                    # 详细数据
                    detail = {
                        **costomer_data,
                        **chat_detail,
                        **inquiry_detail,
                        **order_tracking_detail,
                        **info_number_detail
                    }
                    print(detail)
                    self.save_as_json(detail)
                    print('\n' * 2)
                except Exception as e:
                    self.send_test_log(logName='alibaba 客户资料', logType='Error', msg='{} {} {} {}'.format(self.account, country_code, page, str(e)))
                    print(e)
                    continue
            page += 1
            return self.main(country, page, url_link)
        else:
            # 当前国家客户信息获取完毕后，加到总个数
            self.count += int(total)
            return False

    # 订单跟踪
    def order_tracking(self, customerId):
        print('正在进行订单跟踪')
        order_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/orderQueryServiceI/queryCountOrders.json'
        cycle_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/orderQueryServiceI/queryRepurchaseOrder.json'
        params = {
            'customerId': customerId,
            '_tb_token_': self.tb_token,
            '__t__': str(time.time()).replace('.', '')[:13]
        }
        order_response = requests.get(order_url ,params=params, headers=self.headers)
        cycle_response = requests.get(cycle_url ,params=params, headers=self.headers)
        cycle_data = json.loads(cycle_response.text)['data']
        order_data = json.loads(order_response.text)['data']
        companyTotalAmount = order_data['companyTotalAmount']                 # 累计总金额
        operaterTotalAmount = order_data['operaterTotalAmount']               # 信保总金额
        operaterOngoingCount = order_data['operaterOngoingCount']             # 进行中的信保订单
        companyTotalCount = order_data['companyTotalCount']                   # 累计订单数
        operaterTotalCount = order_data['operaterTotalCount']                 # 信保订单数
        companyOngoingCount = order_data['companyOngoingCount']               # 进行中的公司订单
        cycleDays = cycle_data['cycleDays']                                   # 距离上次购买已经过去
        order_tracking_detail = {
            'companyTotalAmount': companyTotalAmount,
            'operaterTotalAmount': operaterTotalAmount,
            'operaterOngoingCount': operaterOngoingCount,
            'companyTotalCount': companyTotalCount,
            'operaterTotalCount': operaterTotalCount,
            'companyOngoingCount': companyOngoingCount,
            'cycleDays': cycleDays
        }
        return order_tracking_detail

    # 获取在线沟通信息
    def chat_online(self, customerId):
        print('正在获取在线沟通信息')
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/icbuCustomerServiceI/listAtmMessages.json?_tb_token_={}'.format(self.tb_token)
        data = {
            'customerId': customerId
        }
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        datas = json.loads(response.text)['data']['data']
        chat_contents, chat_labels, chat_times, chat_types = [], [], [], []
        if len(datas) != 0:
            for data in datas:
                chat_content = data['content']          # 聊天内容
                chat_label = data['noteLabel']          # 聊天标签
                chat_time = data['noteTime']            # 聊天时间
                chat_type = data['type']                # 聊天类型
                chat_contents.append(chat_content)
                chat_labels.append(chat_label)
                chat_times.append(chat_time)
                chat_types.append(chat_type)

        chat_detail = {
            'chat_content': chat_contents,
            'chat_label': chat_labels,
            'chat_time': chat_times,
            'chat_type': chat_types,
        }
        return chat_detail

    # 获取询盘信息
    def inquiry(self, customerId):
        print('获取询盘信息')
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/icbuCustomerServiceI/listInquiries.json'
        params = {
            'include': 'true',
            'customerId': customerId,
            # 'customerId': 'e5949485309450f201e235be062330db',
            'pageNum': 1,
            'pageSize': 200,
            '_tb_token_': self.tb_token,
            '__t__': str(time.time()).replace('.', '')[:13]
        }
        response = requests.get(url, params=params, headers=self.headers)
        datas = json.loads(response.text)['data']['inquiries']
        inquiry_contents = []
        inquiry_detailSpecs = []
        inquiry_labels = []
        inquiry_times = []
        inquiry_types = []
        if len(datas) != 0:
            for data in datas:
                inquiry_content = data['content']                           # 询盘内容
                inquiry_detailSpec = data['extValues']['detailSpec']        # 起草信保订单链接
                inquiry_label = data['noteLabel']                           # 询盘标签
                inquiry_time = data['noteTime']                             # 询盘时间
                inquiry_type = data['type']                                 # 询盘类型
                inquiry_contents.append(inquiry_content)
                inquiry_detailSpecs.append(inquiry_detailSpec)
                inquiry_labels.append(inquiry_label)
                inquiry_times.append(inquiry_time)
                inquiry_types.append(inquiry_type)
        inquiry_detail = {
            'inquiry_contents': inquiry_contents,
            'inquiry_detailSpecs': inquiry_detailSpecs,
            'inquiry_labels': inquiry_labels,
            'inquiry_times': inquiry_times,
            'inquiry_types': inquiry_types,
        }
        return inquiry_detail

    # 请求获取名片
    def send_name_card(self, contactId ,customerId):
        print('请求获取名片')
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/contactServiceI/applyNameCard.json?_tb_token_={}'.format(self.tb_token)
        data = {
            'contactId': contactId,
            'customerId': customerId
        }
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        print(response)
        print(response.text)

    # 获取用户详情
    def get_info_detail(self, customerId, referenceId):
        # queryCustomerAndContacts.json
        """
        contactId
        customerDetailCO        companyName             公司名称
        customerDetailCO        fax                     传真
        customerDetailCO        annualProcurement       年采购额
        contactQueryCOList      address                 经营地址
        contactQueryCOList      email                   邮箱
        contactQueryCOList      headUrl                 官网
        contactQueryCOList      gender                  性别
        contactQueryCOList      position                职位
        ims:{extValues: {},socialType: "linkedIn",socialValue: "https://www.linkedin.com/in/james-demars-6639a851/"}    社交账号

        :return:
        """
        print('获取用户详情')
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryCustomerAndContacts.json'
        params = {
            'customerId': customerId,
            '_tb_token_': self.tb_token,
            '__t__':  str(time.time()).replace('.', '')[:13]
        }
        response = requests.get(url, headers=self.headers, params=params)
        data = json.loads(response.text)['data']
        annualProcurement = data['customerDetailCO']['annualProcurement']                       # 年采购额
        headUrl = data['contactQueryCOList'][0]['headUrl']                                      # 官网
        address = data['customerDetailCO']['address']
        # district 区    city 市  province 省  street 街道
        country = address['country'] if address['country'] is not  None else '国家未知'
        province = address['province'] if address['province'] is not  None else ' 省未知'
        city = address['city'] if address['city'] is not  None else ' 市未知'
        district = address['district'] if address['district'] is not  None else ' 区未知'
        street = address['street'] if address['street'] is not  None else ' 街道未知'
        business_address = country + province + city + district + street                        # 经营地址
        email = data['contactQueryCOList'][0]['email'][0] if data['contactQueryCOList'][0]['email'] is not None else '-' # 邮箱
        gender = data['contactQueryCOList'][0]['gender']                                        # 性别
        position = data['contactQueryCOList'][0]['position']                                    # 职位
        ims = data['contactQueryCOList'][0]['ims'] if data['contactQueryCOList'][0]['ims'] is not None else {}
        ims_account = str(ims['socialType'] + ' ' + ims['socialValue']) if len(ims) != 0 else '-'       # 社交账号
        contactId = data['contactQueryCOList'][0]['id']
        info_detail = {
            'annualProcurement': annualProcurement,
            'headUrl': headUrl,
            'business_address': business_address,
            'email': email,
            'gender': gender,
            'position': position,
            'ims_account': ims_account,
        }
        number_detail = self.get_number(contactId, customerId, referenceId)
        info_number_detail = {**info_detail, **number_detail}
        return info_number_detail

    # 获取电话号码
    def get_number(self, contactId, customerId, referenceId):
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/contactQueryServiceI/listNameCard.json?_tb_token_={}'.format(self.tb_token)
        data ={
            "nameCardQryList": [
                {
                    "referenceId": referenceId,
                    "contactId": contactId,
                    "customerId": customerId
                }
            ]
        }
        headers = self.headers
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = json.loads(response.text)['data']['data'][0]
        applyStatus = data['applyStatus']                               # 是否发送名片申请
        try:
            mobilePhoneNum = data['mobiles']['mobilePhoneNum'] if data['mobiles'] is not None else '-'             # 电话号码
        except Exception as e:
            print(e)
            print(data)
            sys.exit()
        if applyStatus is not None:
            # 请求获取名片
            self.send_name_card(contactId, customerId)
        applyStatus = '已获取名片信息' if applyStatus is None else '发送请求名片'
        number_detail = {
            'mobilePhoneNum': mobilePhoneNum,
            'send_name_card': applyStatus
        }
        return number_detail

    # 保存到本地
    def save_as_json(self, data):
        with open('customer.csv', 'a', encoding='utf-8', newline='') as f:
            key = ['saleName', 'originSaleName', 'potentialScore', 'customerId', 'companyName', 'aliId', 'loginId', 'buyerID', 'wangwangID', 'referenceId', 'blueTag', 'customerGroup', 'importanceLevel', 'groupName', 'businessType', 'countryCode', 'category', 'customerSource', 'createDate', 'noteTime', 'noteContent', 'willLoss', 'isDing', 'chat_content', 'chat_label', 'chat_time', 'chat_type', 'inquiry_contents', 'inquiry_detailSpecs', 'inquiry_labels', 'inquiry_times', 'inquiry_types', 'companyTotalAmount', 'operaterTotalAmount', 'operaterOngoingCount', 'companyTotalCount', 'operaterTotalCount', 'companyOngoingCount', 'cycleDays', 'annualProcurement', 'headUrl', 'business_address', 'email', 'gender', 'position', 'ims_account', 'mobilePhoneNum', 'send_name_card']
            value = [data[i] for i in key]
            writer = csv.writer(f, dialect='excel')
            writer.writerow(value)
            f.close()


def main():
    account_list = [
        'fb1@jakcom.com',
        # 'fb2@jakcom.com',
        # 'fb3@jakcom.com',
        # 'tx@jakcom.com',
    ]
    url = 'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryCustomerList.json?_tb_token_={}'
    for account in account_list:
        customer = Customer(account)
        country_list = customer.get_all_country()
        country_numbers = len(country_list)
        for index, country in enumerate(country_list[70:]):
            print('当前第个{}国家 共{}个'.format(index, country_numbers))
            try:
                status = customer.main(country, page=1,  url_link=url)
                if status is False:
                    continue
            except Exception as e:
                customer.send_test_log(logName='alibaba 客户列表', logType='Error', msg='{} {} {}'.format(account, country['code'], str(e)))
                continue
        print(customer.count)


if __name__ == '__main__':
    main()