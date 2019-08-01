import time
import sys
import requests
import threading
from flask import Flask, jsonify, request
from aliExpress.album import Album as ExpressAlbum
from photoBank.album import Album as AlibabaAlbum
from aliExpressActivity import storeEvents  # 限时限量折扣    官方活动
from aliExpressActivity import shopDiscount  # 全店铺打折      官方活动
from aliExpressActivity import directionalIssueCoupon  # 定向发放型优惠券

app = Flask(__name__)
account_dict = {}


def custom(account, status, codeType):
    try:
        if codeType == 'aliexpress':
            album = ExpressAlbum(account)
        else:
            album = AlibabaAlbum(account)
        album.main()
        status[account] = None
    except Exception as e:
        print(e)
        status[account] = 'ERROR'
        time.sleep(20)
        status[account] = False


def test(account, status):
    print('aaaa', account_dict)
    time.sleep(20)
    status[account] = None


def finished(account, status):
    time.sleep(20)
    status[account] = False


from alibaba.productionFollowUpDetails import ProductionFollowUpDetails
# 信保订单
@app.route('/get/alibaba/order/process_info')
def productionFollowUpDetails():
    account = request.args.get('account')
    order_id = request.args.get('order_id')
    sku = request.args.get('sku')
    express_info = request.args.get('express_info')
    productionFollowUpDetail = ProductionFollowUpDetails(account, order_id, sku, express_info)
    productionFollowUpDetail.main()


from aliExpressActivity import storeConstruction  # 速卖通店铺装修
@app.route('get/aliexpress/store/decoration')
def storeConstruction():
    account = request.args.get('account')
    store_construction = storeConstruction.main(account)



# 优惠券
@app.route('/get/aliexpress/store_promotion/target_buyerl')
def directionalCoupon():
    account = request.args.get('account')
    buyerID = request.args.get('buyer_id')
    value = request.args.get('value')
    try:
        msg = directionalIssueCoupon.main(account, buyerID, value)
        data = {
            'status': True,
            'msg': msg
        }
    except Exception as e:
        data = {
            'status': True,
            'msg': '创建失败',
            'reason': str(e)
        }
    return jsonify(data)


# 速卖通活动
@app.route('/get/aliexpress/store_promotion/official')
def releaseEvent():
    account_list = request.args.get('account_list')  # 账号列表
    promotion_type = request.args.get('promotion_type')  # 活动类型
    promotion_name = request.args.get('promotion_name')  # 活动名称
    if promotion_type == '限时限量活动':
        print(111)
        msg = storeEvents.main(entrance='FLASK', activity_type=promotion_name, account=account_list)
    else:
        msg = shopDiscount.main(entrance='FLASK', activity_type=promotion_name, account=account_list)
    if msg is not None:
        data = {
            'status': False,
            'promotion_type': promotion_type,
            'promotion_name': promotion_name,
            'msg': msg
        }
        return jsonify(data)
    data = {
        'status': True,
        'promotion_type': promotion_type,
        'promotion_name': promotion_name,
        'msg': 'success' if msg is None else msg
    }
    return jsonify(data)


# 初始化
@app.route('/init')
def init():
    aliExpress_url = 'http://py1.jakcom.it:5000/aliexpress/get/account_cookie/all'
    aliExpressResponse = requests.get(aliExpress_url)
    aliExpressDatas = eval(aliExpressResponse.text)
    account_express_list = aliExpressDatas['all_name']
    account_alibaba_list = [
        'fb1@jakcom.com',
        'fb2@jakcom.com',
        'fb3@jakcom.com',
        'tx@jakcom.com',
    ]
    express_status = {}
    for account_express in account_express_list:
        express_status[account_express] = False
    account_dict['aliexpress'] = express_status
    alibaba_status = {}
    for account_alibaba in account_alibaba_list:
        alibaba_status[account_alibaba] = False
    account_dict['alibaba'] = alibaba_status
    data = {
        'status': True,
        'msg': '初始化成功'
    }
    try:
        if request.method == 'GET':
            return jsonify(data)
    except RuntimeError as e:
        print(data)


# 图片上传
@app.route('/get/<codeType>/store/update_album', methods=['GET'])
def upload_album(codeType):
    account = request.args.get('account')
    try:
        if account not in account_dict[codeType].keys():
            data = {
                'status': False,
                'type': codeType,
                'msg': '请检查账号拼写是否正确'
            }
            return jsonify(data)
        else:
            var = account_dict[codeType][account]
            if var is False:
                account_dict[codeType][account] = True
                expressAlbum = threading.Thread(target=custom, args=(account, account_dict[codeType], codeType))
                expressAlbum.start()
                data = {
                    'status': True,
                    'type': codeType,
                    'account': account,
                    'msg': '开始上传图片'
                }
                return jsonify(data)
            elif var is None:
                finish = threading.Thread(target=finished, args=(account, account_dict[codeType]))
                finish.start()
                data = {
                    'status': True,
                    'type': codeType,
                    'account': account,
                    'msg': '上传图片完成，若需要重新上传，请等待20秒'
                }
                return jsonify(data)
            elif var == 'ERROR':
                data = {
                    'status': True,
                    'type': codeType,
                    'account': account,
                    'msg': '上传失败'
                }
                return jsonify(data)
            else:
                data = {
                    'status': True,
                    'type': codeType,
                    'account': account,
                    'msg': '正在上传中'
                }
                return jsonify(data)
    except KeyError as e:
        print(e)
        data = {
            'status': False,
            'type': codeType,
            'msg': '请先对网站进行初始化(浏览器中输入/init 完成初始化)'
        }
        return jsonify(data)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    init()
    app.run(host='127.0.0.1', port=5000)
