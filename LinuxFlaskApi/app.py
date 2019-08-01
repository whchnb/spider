import datetime
from flask import Flask, jsonify, request
from LinuxFlaskApi.alibaba.updateProduct import main as alibabaUpdateProductMain  # alibaba 在线产品修改
from LinuxFlaskApi.alibaba.updateProductJsonDataGetWithSelenium import main as alibabaUpdateProductTemplateDatasMain  # alibaba 在线产品修改类目模板数据获取


app = Flask(__name__)
"""""""""""""""""""""
alibaba
"""""""""""""""""""""
# alibaba 在线产品修改
@app.route('/get/alibaba/product/modifyProduct')
def alibabaUpdateProduct():
    print(datetime.datetime.now())
    print('alibaba 在线产品修改')
    account = request.args.get('account')
    itemIds = request.args.get('itemIds')
    try:
        msg = alibabaUpdateProductMain(account, itemIds)
        message = {
            'status': True,
            'msg': msg,
        }
        return jsonify(message)
    except Exception as e:
        message = {
            'status': True,
            'msg': '启动失败',
        }
        return jsonify(message)


# alibaba 在线产品修改类目模板数据获取
@app.route('/post/alibaba/category/update_post_data')
def alibabaUpdateProductTemplateDatas():
    try:
        msg = alibabaUpdateProductTemplateDatasMain()
        message = {
            'status': True,
            'msg': msg,
        }
        return jsonify(message)
    except Exception as e:
        message = {
            'status': True,
            'msg': '启动失败',
        }
        return jsonify(message)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='py3.jakcom.it', port=5000)
