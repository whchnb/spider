# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: orderPrinting.py
@time: 2019/6/16 17:52
@desc:  订单打印
"""
import re
import json
import requests
import websocket
import win32print
from urllib.parse import unquote, urlencode
from DynamicAnnouncement.public import Public


class OrderPrinting(Public):
    def __init__(self):
        super(OrderPrinting, self).__init__()
        self.referer_url = self.get_url()

    def get_app_url(self):
        url = 'https://mfuwu.1688.com/offer/getWorkCard.jsonp'
        response = requests.get(url, headers=self.headers)
        datas = response.json()['content']['mainContent']
        for data in datas:
            if data['text'] == '店管家_批量打印发货':
                return data['textUrl']

    # 获取店管家url
    def get_url(self):
        app_url = self.get_app_url()
        # 禁止重定向
        app_response = requests.get(app_url, headers=self.headers, allow_redirects=False)
        managed_url = app_response.headers['Location']
        # print(managed_url)
        managed_response = requests.get(managed_url, headers=self.headers, allow_redirects=False)
        code_url = managed_response.headers['Location']
        # print(code_url)
        code = re.findall(re.compile(r'code=(.*?)&', re.S), unquote(code_url))[0]
        # print(code)
        default_url = 'https://pr1688.dgjapp.com:30009/default.aspx?code=%s' % code
        default_response = requests.get(default_url, headers=self.headers)
        url_re_compile = re.compile(r"href='(.*?)'", re.S)
        url = re.findall(url_re_compile, default_response.text)[0]
        return url

    # 获取memberID
    def get_member_id(self):
        member_id_re_compile = re.compile(r'print_loginid=(.*?)&', re.S)
        member_id = re.findall(member_id_re_compile, self.referer_url)[0]
        return member_id

    def get_template(self):
        url = 'http://pr1688.dgjapp.com/AliAPITools/Common.ashx?FuncName=LoadCommonExpress'
        response = requests.post(url, headers={'referer': self.referer_url})
        template_dict = {i['TemplateName']:i['TemplateId'] for i in response.json()['ResultContent']}
        return template_dict



    # 获取打印机列表
    def get_printer_list(self):
        url = 'http://pr1688.dgjapp.com/AliAPITools/Common.ashx?FuncName=GetPrintBind'
        response = requests.post(url, headers={'Referer': self.referer_url})
        printer_list = response.json()['list']
        printer_dict = {i['TemplateId']:(i['PrinterType'], i['PrintName']) for i in printer_list}
        return printer_dict

    # 获取打印数据
    def get_order_detail(self, templateId, receiver, address, cellphone, tellphone, remark):
        print(self.referer_url)
        url = 'http://pr1688.dgjapp.com/AliAPITools/Common.ashx?FuncName=WayBillRMPrintExpress'
        member_id = self.get_member_id()
        data = {
            'templateId': int(templateId),
            'SellerName': '极控科技',
            'MemberId': member_id,
            'SellerAddress': '山西省太原市迎泽区双塔东街薇彩雅苑1-102   礼品',
            'SellerPhone': '0351-4383818',
            'toFullName': receiver,
            'toArea': address,
            'CompanyName': '山西极控科技有限公司',
            'toCity': '',
            'toMobile': str(cellphone),
            'toPhone': str(tellphone),
            'orderId': '',
            'quantitysum': '',
            'goods': '[{"GoodsName": "%s"}]' % remark,
            'buyerMemberId': '',
            'remark': '',
        }
        response = requests.post(url, data=data, headers={'Referer': self.referer_url})
        order_detail = response.json()['PrintDataList']
        return order_detail

    # 绑定打印机
    def bind(self, printer_data, template_id):
        print(template_id)
        url = ' http://pr1688.dgjapp.com/AliAPITools/Common.ashx?'
        param = {
            'FuncName': 'SavePrintBind',
            'templateId': template_id,
            'printerType': printer_data[0],
            'printName': r'\\192.168.1.11\%s' % printer_data[1].split('\\')[-1] if '192.168' not in printer_data[1] else printer_data[1],
        }
        url = url + urlencode(param)
        response = requests.post(url, headers={'referer': self.referer_url})
        print(response.text)

    # 打印运单
    def print_order(self, templateId, receiver, address, cellphone, tellphone, remark, printerName):
        # 连接打印机
        ws_url = 'ws://127.0.0.1:13528/'
        # ws_url = 'ws://192.168.1.11/:13528'
        ws = websocket.WebSocket()
        ws = websocket.create_connection(ws_url)
        # ws.connect(ws_url)
        request = {
            'requestID': '12345678901234567890',
            'version': '1.0',
            'cmd': 'getPrinters'
        }
        ws.send(json.dumps(request))
        response = ws.recv()
        print(response)
        printer_datas = json.loads(response)['printers']
        printer_dict = {}
        for printer_data in printer_datas:
            if '顺丰' in printer_data['name']:
                printer_dict['顺丰陆运(菜鸟新)'] = printer_data['name']
            elif '圆通' in printer_data['name']:
                printer_dict['圆通自定义(菜鸟新)'] = printer_data['name']
        # print(printer_dict)
        # request = {
        #     'requestID': "12345678901234567890",
        #     'version': "1.0",
        #     'cmd': "GetDefaultPrinterW",
        #     # 'printer': {
        #     #     'name': printer_dict[printerName],
        #     #     # 'name': r'\\127.0.0.1\qr-668-顺丰',
        #     #     'needTopLogo': True,
        #     #     'needBottomLogo': False
        #     # }
        # }
        win32print.SetDefaultPrinter(printer_dict[printerName])
        print(request)
        ws.send(json.dumps(request))
        print(ws.recv())
        # request = {
        #     'requestID': "12345678901234567890",
        #     'version': "1.0",
        #     'cmd': "printerConfig"
        # }
        # ws.send(json.dumps(request))
        # print(ws.recv())
        print(ws.status)
        print(templateId)
        # 打印快递运单
        # 获取需要打印的详细信息
        request = self.get_order_detail(templateId, receiver, address, cellphone, tellphone, remark)
        print(request)
        # # 发送打印请求
        ws.send(json.dumps(request))
        print(ws.recv())
        # 返回快递单号
        waybillNumber = request['task']['documents'][0]['documentID']
        return waybillNumber

    def main(self, printerName, receiver, address, cellphone, tellphone, remark):
        # 获取模板id
        template_dict = self.get_template()
        print(template_dict)
        template_id = str(template_dict[printerName])
        # 获取需要绑定的打印机名称
        # printer_dict = self.get_printer_list()
        # # print(printer_dict)
        # printer_data = printer_dict[template_id]
        # self.bind(printer_data, template_id)

        # 绑定打印机
        # 获取快递公司对应的打印机id

        # 开始打印
        self.print_order(template_id, receiver, address, cellphone, tellphone, remark, printerName)


def main(ship_company, receiver, address, cellphone, tellphone, remark):
    printerName = '圆通自定义(菜鸟新)' if '圆通' in ship_company else '顺丰陆运(菜鸟新)'
    orderPrinting = OrderPrinting()
    orderPrinting.main(printerName, receiver, address, cellphone, tellphone, remark)


if __name__ == '__main__':
    express_delivery_type = [
        '圆通自定义（菜鸟新）',
        '顺丰陆运(菜鸟新)'
    ]
    ship_company = '圆通自定义'
    receiver = 'test'
    address = '北京市'
    cellphone = 12312341234
    tellphone = 12341234567
    remark = 'BH3'
    main(ship_company, receiver, address, cellphone, tellphone, remark)
'''
{'Aisino TY-820II 单打': '435848', 'GP-1324D-圆通': '343734', 'Aisino TY-820II (单打)': '216787', '黑色激光打印机-A4': '0', 'QR-668-顺丰': '352320', 'QR-668 LABEL 顺丰': '352323'}
{'QR-668 LABEL 顺丰': '352323', 'Aisino TY-820II (单打)': '216787', 'GP-1324D-圆通': '343734', 'Aisino TY-820II 单打': '435848', '黑色激光打印机-A4': '0', 'QR-668-顺丰': '352320'}
{'Aisino TY-820II 单打': '435848', 'GP-1324D-圆通': '343734', '黑色激光打印机-A4': '0', 'Aisino TY-820II (单打)': '216787', 'QR-668 LABEL 顺丰': '352323', 'QR-668-顺丰': '352320'}
'''