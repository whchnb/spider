# -*- coding: utf-8 -*- 8:42
import time
import json
import scrapy
import urllib3
import requests
from urllib.parse import urlencode
from oldCustomer.public import Public
from oldCustomer.items import InfoItem, ChatItem, InquiryItem, OlderTrackingItem, InfoDetailItem


n = 0
# from oldCustomer.middlewares import RequestCustomer
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class CustomerSpider(scrapy.Spider):
    name = 'customer'
    allowed_domains = ['alicrm.alibaba.com']
    start_urls = ['https://alicrm.alibaba.com/eggCrmQn/crm/dictionaryQueryServiceI/queryDicList.json']

    # 重写 start_requests
    def start_requests(self):
        account_list = [
            'fb1@jakcom.com',
            'fb2@jakcom.com',
            'fb3@jakcom.com',
            'tx@jakcom.com',
        ]
        country_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/dictionaryQueryServiceI/queryDicList.json?'
        for account in account_list:
            public = Public(account)
            params = {
                'type': 'NATIONAL_AREA',
                '_tb_token_': public.tb_token
            }
            url = country_url + urlencode(params)
            yield scrapy.Request(url=url, callback=self.country_parse, headers=public.headers, meta={'public': public}, dont_filter=True)

    # 获取全部国家
    def country_parse(self, response):
        public = response.meta['public']
        datas = json.loads(response.text)['data']['data']
        url_list = [
            'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryCustomerList.json?_tb_token_={}',
            # 'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryPublicCustomerList.json?_tb_token_={}'
        ]
        for url_link in url_list:
            for data in datas:
                try:
                    country_code = data['code']
                    print(country_code)
                    if country_code != 'jakcom':
                        url = url_link.format(public.tb_token)
                        post_data = {
                            'jsonArray': '[{"id":"664","country_code":"%s"}]' % country_code,
                            'orderDescs': [{'asc': False, 'col': 'opp_gmt_modified'}],
                            'pageNum': 1,
                            'pageSize': 500  # 500
                        }
                        post_response = requests.post(url, headers=public.headers, data=json.dumps(post_data), verify=False)
                        # 获取全部的数据

                        datas = json.loads(post_response.text)['data']['data']
                        # 获取各个国家的客户信息数量
                        total = json.loads(post_response.text)['data']['total']
                        if int(total) % 500 == 0:
                            count = int(total) // 500
                        else:
                            count = int(total) // 500 +1
                        # print(count)
                        for page in range(1, count + 1):
                            post_data = {
                                'jsonArray': '[{"id":"664","country_code":"%s"}]' % country_code,
                                'orderDescs': [{'asc': False, 'col': 'opp_gmt_modified'}],
                                'pageNum': page,
                                'pageSize': 500  # 500
                            }
                            try:
                                yield scrapy.Request(
                                    url=url,
                                    callback=self.parse_customer_info,
                                    headers=public.headers,
                                    body=json.dumps(post_data),
                                    method='POST',
                                    dont_filter=True,
                                    meta={
                                        'public': public,
                                        'country': data,
                                        'page': page
                                    }
                                )
                            except:
                                public.check_cookie()
                                continue
                except Exception as e:
                    print(e)
                    public.check_cookie()

    def parse_customer_info(self, response):
        country = response.meta['country']
        country_code = country['code']
        page = response.meta['page']
        public = response.meta['public']
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
            shops_id_name = {'301001': '锁具零件', '3014': '警卫服务', '301002': '钥匙', '708045': '主板', '301003': '锁匠工具',
                             '3016': '其它安防产品', '708044': '显卡', '708041': '散热系统', '708042': '中央处理器', '100007346': '表盒',
                             '100007347': '拳击球', '100007324': '首饰套装', '100010905': '摄影工作室用品', '100010906': '游戏机支架',
                             '100007323': '戒指', '100010903': '镜头转接环', '100010904': '微型摄像机', '100010901': '相机电池手柄',
                             '100007320': '项链', '100000663': '指甲贴', '5092399': '其它广播&电视附件', '100010916': '电源适配器',
                             '100010912': '耳机配件', '100010909': '便携式收音机', '100010910': '电子阅读器', '127666033': '其他大灯',
                             '303099': '其他门禁产品', '127688045': '智能手环', '100010899': '摄影灯', '100010900': '快门线和遥控器',
                             '100010897': '相机带', '100010898': '柔光罩', '12020305': '汽车喇叭', '100010895': '移动电源',
                             '100010896': '稳定器', '7171': 'USB新奇特', '100010893': '数据线', '7172': '硬盘盒',
                             '100010894': '绕线器', '70803005': '数据交换机', '518': '扬声器', '100000636': '指甲胶水',
                             '5092302': '卫星电视接收器', '523': '传感器', '100000631': '水晶粉', '5092303': '机顶盒',
                             '70803001': '路由器', '70803002': '网络集线器', '70803003': '电脑分享器', '70803004': '网卡',
                             '12020399': '其它汽车电子电器', '7080401': '液晶显示器', '100000603': '沐浴珠', '330801': '人工指甲',
                             '2107': '投影仪', '330808': '指甲烘干机', '2118': '打印机', '127820001': '遥控器', '127820002': '手机',
                             '100009284': '相机闪光灯', '5093004': '手机座', '601': '家用空调', '604': '家用DVD, VCD 播放机',
                             '613': '空气净化器', '100009249': '手写笔', '628': '其它家用电器', '632': '家用收音机', '634': '电视机',
                             '5091005': '电话听筒、耳机', '635': '家庭影院系统', '127756006': '其它显示器', '100001017': '低音喇叭',
                             '100001013': '车载收音机', '100001016': '车载功放', '70802': '键盘', '70803': '调制解调器', '70805': '鼠标',
                             '127818001': '视频眼镜', '70807': '其它存储设备', '361120': '怀表', '2212': '音乐', '5904003': '手机机壳',
                             '5904002': '手机显示屏幕', '1716': '金属工艺品', '127690031': '其他智能家居', '127734058': '扬声器配件',
                             '701': '台式电脑及一体机', '702': '笔记本电脑', '127734060': '智能遥控器', '704': 'PDA', '705': '其它网络设备',
                             '1730': '库存礼品，工艺品', '707': '其它电脑部件', '1735': '礼品套装', '1737': '音乐盒', '717': '其它电脑产品',
                             '720': '机箱', '721': '笔记本散热器', '100006078': '擂台', '5092102': '电视天线', '100006077': '沙包',
                             '100006079': '其它拳击器材', '5092103': '手机天线', '63701': '扩音器', '201153201': '智能安防设备',
                             '63703': '便携式CD播放机', '63704': '数码录音笔', '63705': '耳塞和耳机', '63707': '卡拉OK播放机',
                             '63708': '麦克风', '63710': 'MP3 播放器', '100000433': '充电器', '127678021': 'LED头灯',
                             '100000432': '电池', '370399': '其它家用家具', '70899': '其它电脑附件', '70901': '电脑电源',
                             '190000172': '智能手表', '100010614': '平板电脑', '5090502': '无线广播&电视广播设备', '127654030': '其他汽车配件',
                             '127654029': '其他雾/驾驶灯', '18060304': '游戏光枪', '14190408': '电力电缆', '100000346': '其它零配件',
                             '127694020': '其他的尾灯', '100000344': '电视机支架', '127652033': '灯泡', '380210': '照相机,摄像机包/袋',
                             '5093099': '其他手机配件', '4402': '硬盘播放机', '4403': '古兰经播放器', '4406': '储存卡', '127822001': 'U盘',
                             '63799': '其他家庭音视频设备', '4407': '读卡器', '4408': '屏幕保护膜', '4409': '数码产品清洁用品',
                             '100006482': '车载蓝牙免持听筒套件', '100000335': '蓝光播放机', '380230': '手机包', '380250': 'PDA包',
                             '100002860': '腕表工具和和部件', '711006': '刻录盘', '100002859': '表带', '100001830': '其它节日用品',
                             '190303': '相机滤镜', '190301': '摄影背景', '127684037': '智能手表', '190307': '三脚架', '711004': '光驱',
                             '100002861': '腕表', '711001': '硬盘', '190305': '相机镜头', '711002': '内存', '14190401': '音频/视频线',
                             '1901': '胶片相机', '1902': '摄像机', '100001825': '圣诞装饰', '1908': '胶卷', '1909': '数码相机',
                             '18060399': '其它游戏附件', '100005395': '步程计', '100001788': '贴纸', '120201': '汽车电池',
                             '4499': '其它消费电子产品', '100001791': '其它户外运动玩具', '201148402': '遥控交通工具玩具', '303002': '门禁系统',
                             '303003': '商品电子防盗系统', '100003314': '车载电源转换器', '127660038': '智能配件', '303006': '门禁卡',
                             '303007': '门禁读卡器', '303008': '语音电话', '39050101': '手电筒', '100005845': '其它健身及塑形产品',
                             '708031': '贴纸、皮肤', '100005324': '软驱', '100005330': '工控产品', '708023': '鼠标垫 & 衬垫',
                             '190399': '其它相机附件', '7101': '扫描仪', '100005329': '切换器', '708024': '键盘鼠标套装',
                             '708021': '键盘保护膜', '3008': '警报器', '100005326': '防火墙和VPN', '100005325': '触摸屏显示器',
                             '3010': '锁具', '100005328': '网络机柜', '100005327': '网络存储', '3012': '保险柜'}

            for index, data in enumerate(datas):
                try:
                    print('当前国家{} 当前页数{} 共{}条 正在获取第{}条'.format(country_code, page, numbers, index))
                    saleName = data.get('saleName', '公海客户无业务员')  # 业务员          Ady JAKCOM
                    originSaleName = data['originSaleName'] if data['originSaleName'] is not None else '非公海客户无原业务员'  # 原业务员
                    potentialScore = data.get('potentialScore', '非公海客户无潜力分')  # 潜力分
                    customerId = data['customerId']  # md5 id          3ea91e636c6c565739ce8f69d1ee218f
                    companyName = data['companyName']  # 公司名称
                    aliId = data['mainContact']['aliId']  # 阿里id          133493792210
                    loginId = data['mainContact']['loginId']  # 登录id          sa1340044731celt
                    buyerID = data['mainContact']['contactName']  # 客户姓名
                    wangwangID = data['mainContact'][
                        'wangwangId']  # 旺旺id          8pctgRBMALMfLIST8sj/GVkt8XivkCB66wdkfYSa+s4=
                    referenceId = data['mainContact']['referenceId']  # 参考id          958407859
                    blueTag = data['mainContact']['blueTag']
                    blueTag = blueTag_dict.get(blueTag, blueTag)  # 蓝标            c
                    customerGroup = customerGroup_dict[data['customerGroup']]  # 客户分组     customerGroup_list
                    importanceLevel = data['importanceLevel']  # 重要星级      0 未设置       1 1星    2 2星    3 3星
                    groupName = '未设置分群' if data['marketingGroups'] is None else data['marketingGroups'][0][
                        'groupName']  # 客户分群
                    businessTypes = data['businessTypes']
                    businessType = ','.join([businessTypes_dict[i] for i in businessTypes]) if len(
                        businessTypes) != 0 else '未设置商业类型'  # 商业类型      businessTypes_dict
                    countryCode = data['countryCode']  # 国家地区
                    categorys = data['categorys']
                    category = ','.join([shops_id_name.get(category, '-') for category in categorys]).replace('-,',
                                                                                                              '') if len(
                        categorys) != 0 else '无采购品类'  # 采购品类      shops_id_name
                    customerSources = data['customerSources']
                    customerSource = ','.join([customerSources_dict.get(i, i) for i in customerSources]) if len(
                        customerSources) != 0 else '客户来源未知'  # 客户来源      customerSources_dict
                    createDate = data['createDate']  # 建档时间
                    noteTime = data['recentNote']['noteTime'] if data['recentNote'] is not None else None  # 小计时间
                    noteContent = data['recentNote']['content'] if data['recentNote'] is not None else None  # 跟进小记
                    willLoss = willLoss_dict[data.get('willLoss', '非公海客户无流失预警')]  # 流失预警
                    isDing = data.get('isDing', '非公海客户无钉住状态')  # 钉住状态
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
                        'account': public.account
                    }
                    # 获取订单跟踪信息
                    order_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/orderQueryServiceI/queryCountOrders.json'
                    order_oparams = {
                        'customerId': customerId,
                        '_tb_token_': public.tb_token,
                        '__t__': str(time.time()).replace('.', '')[:13]
                    }
                    oredr_full_url = order_url + '?' + urlencode(order_oparams)
                    yield scrapy.Request(
                        url=oredr_full_url,
                        headers=public.headers,
                        dont_filter=True,
                        callback=self.order_tracking,
                        meta={
                            'type': 'order',
                            'public': public,
                            'customerId': customerId
                        }
                    )
                    cycle_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/orderQueryServiceI/queryRepurchaseOrder.json'
                    cycle_full_url = cycle_url + '?' + urlencode(order_oparams)
                    yield scrapy.Request(
                        url=cycle_full_url,
                        headers=public.headers,
                        dont_filter=True,
                        callback=self.order_tracking,
                        meta={
                            'type': 'cycle',
                            'public': public,
                            'customerId': customerId
                        }
                    )
                    # self.order_tracking(customerId, public)
                    # 获取客户详细信息
                    info_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryCustomerAndContacts.json'
                    info_params = {
                        'customerId': customerId,
                        '_tb_token_': public.tb_token,
                        '__t__': str(time.time()).replace('.', '')[:13]
                    }
                    info_full_url = info_url + '?' + urlencode(info_params)
                    yield scrapy.Request(
                        url=info_full_url,
                        headers=public.headers,
                        dont_filter=True,
                        callback=self.get_info_detail,
                        meta={
                            'type': 'cycle',
                            'public': public,
                            'customerId': customerId,
                            'referenceId': referenceId
                        }
                    )
                    # self.get_info_detail(customerId, referenceId, public)
                    # 详细数据
                    detail = {
                        **costomer_data,
                        # **info_number_detail
                    }
                    info= InfoItem()
                    for k, v in detail.items():
                        info[k] = v
                    yield info
                    # 获取在线聊天内容
                    chat_online_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/icbuCustomerServiceI/listAtmMessages.json?_tb_token_={}'.format(
                        public.tb_token)
                    chat_online_data = json.dumps({'customerId': customerId})
                    yield scrapy.Request(
                        url=chat_online_url,
                        callback=self.chat_online,
                        headers=public.headers,
                        dont_filter=True,
                        body=chat_online_data,
                        method='POST',
                        meta={
                            'public': public,
                            'customerId': customerId
                        }
                    )
                    # 获取询盘信息
                    inquiry_url ='https://alicrm.alibaba.com/eggCrmQn/crm/icbuCustomerServiceI/listInquiries.json?'
                    inquiry_params = {
                        'include': 'true',
                        'customerId': customerId,
                        'pageNum': 1,
                        'pageSize': 200,
                        '_tb_token_': public.tb_token,
                        '__t__': str(time.time()).replace('.', '')[:13]
                    }
                    inquiry_full_url = inquiry_url + urlencode(inquiry_params)
                    yield scrapy.Request(
                        url=inquiry_full_url,
                        callback=self.inquiry,
                        dont_filter=True,
                        headers=public.headers,
                        meta={
                            'public': public,
                            'customerId': customerId
                        }
                    )
                except Exception as e:
                    print(e)
                    public.check_cookie()
                    continue




    # 获取在线沟通信息
    def chat_online(self, response):
        customerId = response.meta['customerId']
        public = response.meta['public']
        try:
            datas = json.loads(response.text)['data']['data']
            if len(datas) != 0:
                for data in datas:
                    chat = ChatItem()
                    chat['chat_contents'] = data['content']  # 聊天内容
                    chat['chat_labels'] = data['noteLabel']  # 聊天标签
                    chat['chat_times'] = data['noteTime']  # 聊天时间
                    chat['chat_types'] = data['type']  # 聊天类型
                    chat['Customer_md5'] = customerId
                    chat['account'] = public.account
                    yield chat
        except Exception as e:
            print(e)
            public.check_cookie()

    # 获取询盘信息
    def inquiry(self, response):
        if type(response) is not str:
            print(response.text)
            datas = json.loads(response.text)['data']['inquiries']
            public = response.meta['public']
            customerId = response.meta['customerId']
            if len(datas) != 0:
                for data in datas:
                    try:
                        inquiry = InquiryItem()
                        inquiry['inquiry_contents'] = data['content']  # 询盘内容
                        inquiry['inquiry_detailSpecs'] = data['extValues']['detailSpec']  # 起草信保订单链接
                        inquiry['inquiry_labels'] = data['noteLabel']  # 询盘标签
                        inquiry['inquiry_times'] = data['noteTime']  # 询盘时间
                        inquiry['inquiry_types'] = data['type']  # 询盘类型
                        inquiry['Customer_md5'] = customerId  # md5id
                        inquiry['account'] = public.account  # 账户
                        yield inquiry
                    except Exception as e:
                        print(e)
                        public.check_cookie()

    # 订单跟踪
    def order_tracking(self, response):
        t = response.meta['type']
        public = response.meta['public']
        customerId = response.meta['customerId']
        item = OlderTrackingItem()
        try:
            if t == 'order':
                #
                order_data = json.loads(response.text)['data']
                companyTotalAmount = order_data['companyTotalAmount']  # 累计总金额
                operaterTotalAmount = order_data['operaterTotalAmount']  # 信保总金额
                operaterOngoingCount = order_data['operaterOngoingCount']  # 进行中的信保订单
                companyTotalCount = order_data['companyTotalCount']  # 累计订单数
                operaterTotalCount = order_data['operaterTotalCount']  # 信保订单数
                companyOngoingCount = order_data['companyOngoingCount']  # 进行中的公司订单

                order_tracking_detail = {
                    'companyTotalAmount': companyTotalAmount,
                    'operaterTotalAmount': operaterTotalAmount,
                    'operaterOngoingCount': operaterOngoingCount,
                    'companyTotalCount': companyTotalCount,
                    'operaterTotalCount': operaterTotalCount,
                    'companyOngoingCount': companyOngoingCount,
                    'account': public.account,
                    'customerId' : customerId

                }
            else:
                cycle_data = json.loads(response.text)['data']
                cycleDays = cycle_data['cycleDays']  # 距离上次购买已经过去
                order_tracking_detail = {
                    'cycleDays': cycleDays,
                    'account': public.account,
                    'customerId': customerId

                }
            for k, v in order_tracking_detail.items():
                item[k] = v
            yield item
            # return order_tracking_detail
        except Exception as e:
            print(e)
            public.check_cookie()

    # 请求获取名片
    def send_name_card(self, response):
        public = response.meta['public']
        # url = 'https://alicrm.alibaba.com/eggCrmQn/crm/contactServiceI/applyNameCard.json?_tb_token_={}'.format(
        #     public.tb_token)
        # data = {
        #     'contactId': contactId,
        #     'customerId': customerId
        # }
        # response = requests.post(url, data=json.dumps(data), headers=public.headers, verify=False)
        try:
            status = json.loads(response.text)['data']['data']
            if status is True:
                print('请求获取名片信息发送成功')
        except Exception as e:
            print(e)
            public.check_cookie()

    # 获取用户详情
    def get_info_detail(self, response):
        print('获取用户详情')
        # print(response.url)
        item = InfoDetailItem()
        public = response.meta['public']
        customerId = response.meta['customerId']
        referenceId = response.meta['referenceId']
        data = json.loads(response.text)['data']


        # annualProcurement = data['customerDetailCO']['annualProcurement']  # 年采购额
        # headUrl = data['contactQueryCOList'][0]['headUrl']  # 官网
        # address = data['customerDetailCO']['address']
        # # district 区    city 市  province 省  street 街道
        # country = address['country'] if address['country'] is not None else '国家未知'
        # province = address['province'] if address['province'] is not None else ' 省未知'
        # city = address['city'] if address['city'] is not None else ' 市未知'
        # district = address['district'] if address['district'] is not None else ' 区未知'
        # street = address['street'] if address['street'] is not None else ' 街道未知'
        # business_address = country + province + city + district + street  # 经营地址
        # try:
        #     email = data['contactQueryCOList'][0]['email'][0] if data['contactQueryCOList'][0][
        #                                                              'email'] is not None else '-'  # 邮箱
        # except:
        #     email = '-'
        # gender = data['contactQueryCOList'][0]['gender']  # 性别
        # position = data['contactQueryCOList'][0]['position']  # 职位
        # try:
        #     ims = data['contactQueryCOList'][0]['ims'] if data['contactQueryCOList'][0]['ims'] is not None else {}
        #     ims_account = str(ims['socialType'] + ' ' + ims['socialValue']) if len(ims) != 0 else '-'  # 社交账号
        # except:
        #     ims_account = '-'
        # contactId = data['contactQueryCOList'][0]['id']
        # info_detail = {
        #     'annualProcurement': annualProcurement,
        #     'headUrl': headUrl,
        #     'business_address': business_address,
        #     'email': email,
        #     'gender': gender,
        #     'position': position,
        #     'ims_account': ims_account,
        #     'account': public.account,
        #     'customerId': customerId
        #
        # }
        # number_detail = self.get_number(contactId, customerId, referenceId, public)
        # info_number_detail = {**info_detail, **number_detail}
        # print(info_number_detail)
        # for k, v in info_number_detail.items():
        #     print(k,v)
        #     item[k] = v
        # yield item



        try:
            annualProcurement = data['customerDetailCO']['annualProcurement']  # 年采购额
            headUrl = data['contactQueryCOList'][0]['headUrl']  # 官网
            address = data['customerDetailCO']['address']
            # district 区    city 市  province 省  street 街道
            country = address['country'] if address['country'] is not None else '国家未知'
            province = address['province'] if address['province'] is not None else ' 省未知'
            city = address['city'] if address['city'] is not None else ' 市未知'
            district = address['district'] if address['district'] is not None else ' 区未知'
            street = address['street'] if address['street'] is not None else ' 街道未知'
            business_address = country + province + city + district + street  # 经营地址
            try:
                email = data['contactQueryCOList'][0]['email'][0] if data['contactQueryCOList'][0][
                                                                         'email'] is not None else '-'  # 邮箱
            except:
                email = '-'
            gender = data['contactQueryCOList'][0]['gender']  # 性别
            position = data['contactQueryCOList'][0]['position']  # 职位
            try:
                ims = data['contactQueryCOList'][0]['ims'] if data['contactQueryCOList'][0]['ims'] is not None else {}
                ims_account = str(ims['socialType'] + ' ' + ims['socialValue']) if len(ims) != 0 else '-'  # 社交账号
            except:
                ims_account = '-'
            contactId = data['contactQueryCOList'][0]['id']
            info_detail = {
                'annualProcurement': annualProcurement,
                'headUrl': headUrl,
                'business_address': business_address,
                'email': email,
                'gender': gender,
                'position': position,
                'ims_account': ims_account,
                'account': public.account,
                'customerId': customerId

            }
            number_detail = self.get_number(contactId, customerId, referenceId, public)
            info_number_detail = {**info_detail, **number_detail}
            for k, v in info_number_detail.items():
                item[k] = v
            yield item
        except Exception as e:
            print(e)
            print(response.text)
            public.check_cookie()


    def send(self, public, contactId, customerId):
        name_card_url = 'https://alicrm.alibaba.com/eggCrmQn/crm/contactServiceI/applyNameCard.json?_tb_token_={}'.format(
            public.tb_token)
        data = {
            'contactId': contactId,
            'customerId': customerId
        }
        yield scrapy.Request(
            url=name_card_url,
            callback=self.send_name_card,
            headers=public.headers,
            dont_filter=True,
            method=['POST'],
            body=json.dumps(data),
            meta={
                'public': public
            }
        )


    # 获取电话号码
    def get_number(self, contactId, customerId, referenceId, public):
        url = 'https://alicrm.alibaba.com/eggCrmQn/crm/contactQueryServiceI/listNameCard.json?_tb_token_={}'.format(
            public.tb_token)
        data = {
            "nameCardQryList": [
                {
                    "referenceId": referenceId,
                    "contactId": contactId,
                    "customerId": customerId
                }
            ]
        }
        headers = public.headers
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
            data = json.loads(response.text)['data']['data'][0]
            applyStatus = data['applyStatus']  # 是否发送名片申请
            try:
                mobilePhoneNum = data['mobiles']['mobilePhoneNum'] if data['mobiles'] is not None else '-'  # 电话号码
            except Exception as e:
                print(e)
                print(data)
                sys.exit()
            if applyStatus is not None:
                # 请求获取名片
                self.send(public, contactId, customerId)
                # self.send_name_card(contactId, customerId, public)
            applyStatus = '已获取名片信息' if applyStatus is None else '发送请求名片'
            number_detail = {
                'mobilePhoneNum': mobilePhoneNum,
                'send_name_card': applyStatus
            }
            return number_detail
        except Exception as e:
            print(e)
            public.check_cookie()



if __name__ == '__main__':
    import sys, os
    from scrapy.cmdline import execute

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    execute(['scrapy', 'crawl', 'customer'])
