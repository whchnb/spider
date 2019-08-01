# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: upload_album.py
@time: 2019/5/27 18:39
@desc:
"""
from flask import Blueprint,request,render_template,send_from_directory,jsonify,session


maincontroller=Blueprint('maincontroller',__name__)
@maincontroller.route('/get/aliexpress/store/update_album')
def album_upload():
    pass