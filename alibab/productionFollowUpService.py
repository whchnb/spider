# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: productionFollowUpService.py
@time: 2019/6/5 17:58
@desc:
"""
import time
import json
import requests
from urllib.parse import urlencode
from alibaba.public import Public


class ProductionFollowUpService(Public):
    def __init__(self, account):
        self.account = account
        super(ProductionFollowUpService, self).__init__(self.account)

    def get_single_number(self, page=1):

        url = 'https://onetouch.alibaba.com/moSurvey/schedule/list2.json?'
        params = {
            'json': json.dumps({
                "currentPage": page,
                "pageSize": 20,
                "sort": {},
                "orderBy": "RANK",
                "secondRankName": "tracking_service_warning_order",
                "status": "tracking_service_wait_for_checking",
                "descSort": True})
        }
        url += urlencode(params)
        response = requests.get(url, headers=self.headers)
        responseDatas = json.loads(response.text)['data']
        totalPage = responseDatas['totalPage']
        print(responseDatas)
        print(totalPage)
        if page > totalPage:
            return
        else:
            postUrl = 'http://py1.jakcom.it:5000/alibaba/post/order/update_process_info'
            datas = responseDatas['dataList']
            templateItemNameKey_dict = {"placeholder.expectFinishedDate": "请选择计划完成日期", "placeholder.remark": "请输入备注",
                                        "orderSchedule.task.templateName.taScheduleCloth.packageCompletion": "包装完成",
                                        "orderSchedule.task.templateName.taScheduleCloth.detectionCompletion": "检测完成",
                                        "orderSchedule.task.templateName.taScheduleCloth.materialPreparing": "备料入仓",
                                        "orderSchedule.task.templateName.taScheduleCloth.productionCompletion": "生产完成",
                                        "orderSchedule.task.templateName.taScheduleCloth.shipment": "出货",
                                        "orderSchedule.task.templateName.taScheduleCloth.productionStart": "生产开始",
                                        "orderSchedule.task.templateName.amzs.yangpin": "样品照片上传",
                                        "orderSchedule.task.templateName.amzs.dabaotiewaibia": "打包贴外标",
                                        "orderSchedule.task.templateName.amzs.dianshangziyuanbao": "电商资源包分享",
                                        "orderSchedule.task.templateName.amzs.tieneibia": "帖内标",
                                        "orderSchedule.task.templateName.amzs.jiancha": "检测完成",
                                        "orderSchedule.task.templateName.amzs.fahuo": "发货信息采集",
                                        "orderSchedule.task.templateName.taScheduleGeneral.detectionCompletion": "检测完成",
                                        "orderSchedule.task.templateName.taScheduleGeneral.packageCompletion": "包装完成",
                                        "orderSchedule.task.templateName.taScheduleGeneral.productionCompletion": "生产完成",
                                        "orderSchedule.task.templateName.taScheduleGeneral.shipment": "发货信息采集",
                                        "orderSchedule.task.templateName.taScheduleGeneral.shipment.button": "去发货",
                                        "orderSchedule.task.templateName.taScheduleGeneral.materialPreparing": "备料入仓",
                                        "orderSchedule.task.templateName.taScheduleGeneral.productionStart": "开始生产",
                                        "orderSchedule.task.templateName.loaded": "发货",
                                        "orderSchedule.task.templateName.knitting.zhuanghuo": "装货",
                                        "orderSchedule.task.templateName.knitting.xishui": "洗水",
                                        "orderSchedule.task.templateName.knitting.beiliao": "备料",
                                        "orderSchedule.task.templateName.knitting.fenghe": "套口缝合/手缝",
                                        "orderSchedule.task.templateName.knitting.baozhuang": "包装",
                                        "orderSchedule.task.templateName.knitting.bianzhi": "横机编织",
                                        "orderSchedule.task.templateName.knitting.houdao": "后道",
                                        "orderSchedule.task.templateName.3c.zhusu": "注塑",
                                        "orderSchedule.task.templateName.3c.baozhuang": "包装",
                                        "orderSchedule.task.templateName.3c.zhuanghuo": "装货",
                                        "orderSchedule.task.templateName.3c.tiepian": "贴片",
                                        "orderSchedule.task.templateName.3c.beiliao": "备料",
                                        "orderSchedule.task.templateName.3c.test": "老化测试",
                                        "orderSchedule.task.templateName.3c.zuzhuang": "组装",
                                        "orderSchedule.task.templateName.start30": "成品制定完成",
                                        "orderSchedule.task.templateName.start10": "布匹裁剪完成",
                                        "orderSchedule.task.templateName.clothing.zhuanghuo": "装货",
                                        "orderSchedule.task.templateName.clothing.houdao": "后道",
                                        "orderSchedule.task.templateName.clothing.baozhuang": "包装",
                                        "orderSchedule.task.templateName.clothing.beiliao": "备料",
                                        "orderSchedule.task.templateName.clothing.caifeng": "剪裁",
                                        "orderSchedule.task.templateName.clothing.fengren": "缝纫",
                                        "orderSchedule.task.templateName.start50": "烫染完成",
                                        "orderSchedule.task.templateName.start": "开始",
                                        "orderSchedule.task.templateName.default.packing": "包装",
                                        "orderSchedule.task.templateName.default.progressA": "生产A",
                                        "orderSchedule.task.templateName.default.progressB": "生产B",
                                        "orderSchedule.task.templateName.default.start": "备料",
                                        "orderSchedule.task.templateName.default.loading": "装货",
                                        "orderSchedule.task.templateName.finish": "打包装箱完成",
                                        "orderSchedule.task.buyer.view": "此环节买家查看次数",
                                        "orderSchedule.taOrderList.tracking_service_finished": "已完成",
                                        "orderSchedule.taOrderList.paymentStatus.ADVANCE": "预付款",
                                        "orderSchedule.taOrderList.paymentStatus.FULL": "全款",
                                        "orderSchedule.taOrderList.paymentStatus.BALANCE": "未付款",
                                        "orderSchedule.taOrderList.paymentStatus.NOT_PAY": "未付款",
                                        "orderSchedule.taOrderList.tracking_service_wait_for_checking": "进行中",
                                        "orderSchedule.firstLevel.desc.Agriculture": "农业",
                                        "orderSchedule.firstLevel.desc.Machinery": "机械",
                                        "orderSchedule.firstLevel.desc.Electrical_Equipment_Supplies": "电气设备及用品",
                                        "orderSchedule.firstLevel.desc.Lights_Lighting": "灯光和照明",
                                        "orderSchedule.firstLevel.desc.Office_School_Supplies": "办公文教用品",
                                        "orderSchedule.firstLevel.desc.Fashion_Accessories": "时尚饰品",
                                        "orderSchedule.firstLevel.desc.Chemicals": "化学物质",
                                        "orderSchedule.firstLevel.desc.Apparel": "服装",
                                        "orderSchedule.firstLevel.desc.Minerals_Metallurgy": "矿产和冶金",
                                        "orderSchedule.firstLevel.desc.Health_Medical": "健康与医疗",
                                        "orderSchedule.firstLevel.desc.Business_Services": "商业服务",
                                        "orderSchedule.firstLevel.desc.Sports_Entertainment": "体育和娱乐",
                                        "orderSchedule.firstLevel.desc.Fabrication_Services": "制造服务",
                                        "orderSchedule.firstLevel.desc.Textiles_Leather_Products": "纺织及皮革制品",
                                        "orderSchedule.firstLevel.desc.Food_Beverage": "食品和饮料",
                                        "orderSchedule.firstLevel.desc.Rubber_Plastics": "橡塑原料及制品",
                                        "orderSchedule.firstLevel.desc.Beauty_Personal_Care": "美容及个人护理",
                                        "orderSchedule.firstLevel.desc.Service_Equipment": "维修设备",
                                        "orderSchedule.firstLevel.desc.Furniture": "家具",
                                        "orderSchedule.firstLevel.desc.Gifts_Crafts": "礼品和工艺品",
                                        "orderSchedule.firstLevel.desc.Timepieces_Jewelry_Eyewear": "钟表、珠宝、眼镜",
                                        "orderSchedule.firstLevel.desc.Construction_Real_Estate": "建筑与房地产",
                                        "orderSchedule.firstLevel.desc.Electronic_Components_Supplies": "电子元件及用品",
                                        "orderSchedule.firstLevel.desc.Home_Appliances": "家用电器",
                                        "orderSchedule.firstLevel.desc.Luggage_Bags_Cases": "行李，袋子和箱子",
                                        "orderSchedule.firstLevel.desc.Packaging_Printing": "包装与印刷",
                                        "orderSchedule.firstLevel.desc.Toys_Hobbies": "玩具",
                                        "orderSchedule.firstLevel.desc.Environment": "环境",
                                        "orderSchedule.firstLevel.desc.Vehicles_Accessories": "车辆及配件",
                                        "orderSchedule.firstLevel.desc.Home_Garden": "家居与园艺",
                                        "orderSchedule.firstLevel.desc.Telecommunications": "电信",
                                        "orderSchedule.firstLevel.desc.Energy": "能源",
                                        "orderSchedule.firstLevel.desc.Security_Protection": "安全防护",
                                        "orderSchedule.firstLevel.desc.Shoes_Accessories": "鞋子和配件",
                                        "orderSchedule.firstLevel.desc.Consumer_Electronics": "消费电子",
                                        "orderSchedule.firstLevel.desc.Tools_Hardware": "工具和硬件",
                                        "orderSchedule.taskStatus.task_finished": "完成",
                                        "orderSchedule.taskStatus.wait_for_checking": "等待中",
                                        "orderSchedule.taskStatus.task_fail": "无法办理",
                                        "orderSchedule.taskStatus.all": "全部",
                                        "orderSchedule.produceProgressStatus.shipping_finish": "-",
                                        "orderSchedule.produceProgressStatus.order_finish": "-",
                                        "orderSchedule.produceProgressStatus.warning": "预警",
                                        "orderSchedule.produceProgressStatus.delay": "超期",
                                        "orderSchedule.produceProgressStatus.normal": "正常",
                                        "orderSchedule.reviewTaskStatus.wait_for_feedback": "待反馈",
                                        "orderSchedule.reviewTaskStatus.finish_evaluate": "已评价",
                                        "orderSchedule.reviewTaskStatus.wait_for_evaluate": "未评价",
                                        "orderSchedule.reviewTaskStatus.finished": "已反馈",
                                        "orderSchedule.rejectReason.image_not_true": "虚假拍摄",
                                        "orderSchedule.rejectReason.other_reason": "其他原因",
                                        "orderSchedule.rejectReason.location_distance_terrible": "地址偏差过大",
                                        "orderSchedule.rejectReason.inventory_product": "产品是库存产品",
                                        "orderSchedule.rejectReason.not_suit_for_order": "拍摄内容与订单不符",
                                        "orderSchedule.rejectReason.over_produt_time": "实际生产进度已超过当前阶段",
                                        "orderSchedule.rejectReason.image_or_video_not_uploaded": "未上传图片或视频",
                                        "orderSchedule.rejectReason.uploaded_image_or_video_unqualified": "已上传图片或视频不合格",
                                        "orderSchedule.rejectReason.no_enough_photo_employee": "未能安排拍摄人员",
                                        "orderSchedule.rejectReason.schedule_dely": "进度延期",
                                        "orderSchedule.rejectReason.not_ship_to_specified_warehouse": "未发货至指定海外仓",
                                        "orderSchedule.fail.mustLogin": "必须先登录才能操作",
                                        "orderSchedule.fail.noPermision": "无权操作该信保单",
                                        "orderSchedule.fail.paramError": "参数错误",
                                        "orderSchedule.fail.sysException": "系统异常",
                                        "orderSchedule.feedbackStatus.finished": "已反馈",
                                        "orderSchedule.feedbackStatus.wait_for_feedback": "待反馈",
                                        "orderSchedule.detail.product.name": "产品名称",
                                        "orderSchedule.detail.product.quantity": "数量",
                                        "orderSchedule.detail.product.description": "描述",
                                        "ta.schedule.task.template.resolver.eCommerceService": "电商一站通",
                                        "ta.schedule.task.template.resolver.eCommerceService.desc": "从定制、检测、打包贴标到发货一站式服务",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral": "生产可视化",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral.simple": "生产可视化简易版",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral.desc": "生产型订单监控",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral.closed": "The order has been closed and order tracking service is not available. \n",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral.simpleMode.desc": "生产可视化简易模版描述",
                                        "ta.schedule.task.template.resolver.taScheduleGeneral.defaultMode.desc": "生产可视化模版描述",
                                        "ta.schedule.task.template.resolver.1200000212": "生产可视化",
                                        "ta.schedule.task.template.resolver.default": "默认类型",
                                        "ta.schedule.task.template.resolver.clothing": "服装",
                                        "ta.schedule.task.template.resolver.3c": "消费电子",
                                        "ta.schedule.task.template.resolver.knitting": "针织工艺",
                                        "ta.schedule.task.template.type": "可视化类型",
                                        "ta.schedule.page.createOrder.buyer.deliver.content": "供应商已发货，服务无法开启，更多了解",
                                        "ta.schedule.page.createOrder.buyer.deliver.content.rax": "供应商已发货，服务无法开启。",
                                        "ta.schedule.page.createOrder.buyer.deliver.title": "提示",
                                        "ta.schedule.page.createOrder.seller.deliver.content": "货物已发出，服务不能被开启。请在发货前开启订单可视化服务。",
                                        "ta.schedule.ta.order.relative.prepayment.expect.shipping.time": "预付款收齐到账duration天后发货",
                                        "ta.schedule.ta.order.relative.prepayment.expect.deliveryTime": "计划发货时间",
                                        "ta.schedule.ta.order.relative.prepayment.expect.deliveryStatus": "发货状态",
                                        "ta.schedule.ta.order.relative.prepayment.deliveryTime": "实际发货时间",
                                        "ta.schedule.ta.order.relative.all.payment.expect.shipping.time": "全款到账收齐duration天后发货",
                                        "ta.schedule.ta.order.relative.balance.payment.expect.shipping.time": "全款收齐后duration天后发货",
                                        "seller.show.buyer.view.num": "买家访问次数",
                                        "rax.buyer.submitted": "供应商已敦促及时上传最新生产情况。", "rax.buyer.header.title": "生产服务跟进",
                                        "rax.buyer.header.content.second": "如果延期仍未收到状态更新，或有其他问题，请联系供应商。",
                                        "rax.buyer.header.content.first": "供应商将按约定生产线上传图片。",
                                        "rax.buyer.header.confirmed": "待卖家确认", "rax.buyer.leave.comment": "联系供应商",
                                        "rax.buyer.select.tracking.steps": "选择生产跟进服务类型（多选）",
                                        "rax.buyer.select.one.multiple": "请选择一个或多个选项",
                                        "rax.buyer.preview.tracking": "预览生产跟进步骤",
                                        "rax.buyer.service.enabled": "服务未开启，联系供应商或者去PC端开启服务。",
                                        "rax.buyer.estimated.time": "预计完成时间", "rax.buyer.review": "评价",
                                        "rax.buyer.reminderText": "Note that order tracking only begins once initial payment has been made. ",
                                        "rax.buyer.remind.supplier": "提醒供应商",
                                        "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].IN_SHIPPING": "发货中",
                                        "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].WAIT_TO_SHIPPING": "等待发货",
                                        "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].BUYER_SIGN": "买家签收",
                                        "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].CLOSE": "订单关闭",
                                        "deliveryCenter.deliveryHome.deliveryStatus.[ENUM].FINISH": "发货完成",
                                        "deliveryCenter.deliveryHome.deliveryStatus.ENUM].SELLER_SIGN": "卖家签收"}
            for data in datas:
                try:
                    taOrderNo = data['taOrderNo']  # 信单保号
                    if int(taOrderNo) == 14187703501026916:
                        print(data)
                    buyerName = data['buyerName']  # 买家名称
                    gmtCreate = data['gmtCreate']  # 创建时间
                    templateItemNameKey = templateItemNameKey_dict.get(data['templateItemNameKey'], '未获取到样品状态')  # 样品状态
                    localTime = data['expectShippingTime']
                    expectShippingTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                        int(str(localTime)[:10]))) if localTime is not None else ''  # 计划发货时间
                    status = templateItemNameKey_dict.get('orderSchedule.taOrderList.' + data['status'],
                                                          '未获取到办理状态')  # 办理状态
                    currentOwner = data['currentOwner']  # 当前负责人
                    buyerViewOrNot = '是' if data['buyerViewOrNot'] is True else '否'  # 买家是否查看
                    paymentStatusKey = templateItemNameKey_dict[data['paymentStatusKey']]  # 付款状态
                    produceProgressStatus = templateItemNameKey_dict.get(
                        'orderSchedule.produceProgressStatus.' + data['produceProgressStatus'], '未获取到进度提醒')  # 进度提醒
                    gmtTaskExpectFinished = data['gmtTaskExpectFinished'] if data[
                                                                                 'gmtTaskExpectFinished'] is not None else ''  # 当前节点计划完成时间
                    postData = {
                        'Account': self.account,
                        'TA_Order_ID': taOrderNo,
                        'Buyer_Name': buyerName,
                        'Create_Time': gmtCreate,
                        'Progress_Rate': templateItemNameKey,
                        'Sent_Time': expectShippingTime,
                        'Process_Status': status,
                        'Principal': currentOwner,
                        'View_Status': buyerViewOrNot,
                        'Remind_Status': produceProgressStatus,
                        'Step_Time': gmtTaskExpectFinished,
                        'Payment_Status': paymentStatusKey
                    }
                    print(postData)
                    postResponse = requests.post(postUrl, postData)
                    print(postResponse)
                    print(postResponse.text)
                except Exception as e:
                    print(e)
                    continue
            page += 1
            return self.get_single_number(page=page)

    def main(self):
        self.get_single_number()


def main():
    account_list = [
        # 'fb1@jakcom.com',
        'fb2@jakcom.com',
        'fb3@jakcom.com',
        'tx@jakcom.com',
    ]
    for account in account_list:
        productionFollowUpService = ProductionFollowUpService(account)
        productionFollowUpService.main()
        # url = 'https://onetouch.alibaba.com/moSurvey/schedule/list2.json?'
        # params = {
        #     'json': {"taOrderNo":"14187703501026916","currentPage":1,"pageSize":10,"sort":{},"orderBy":"RANK","secondRankName":"tracking_service_warning_order","descSort":True}
        # }
        # url += urlencode(params)
        # response = requests.get(url, productionFollowUpService.headers)
        # print(response)
        # print(response.text)


if __name__ == '__main__':
    main()
