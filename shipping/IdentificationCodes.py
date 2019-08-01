# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: IdentificationCodes.py
@time: 2019/6/20 10:58
@desc:
"""
import sys
import requests
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class IdentificationCodes(object):
    # 保存验证码
    def get_img(self, url, headers):
        r = requests.get(url, headers=headers)
        with open('get_image.jpg', 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            f.close()

    def identification(self, url=None, headers=None, t=None):
        try:
            if url is not None:
                self.get_img(url, headers)
            img = Image.open('get_image.jpg') # PIL库加载图片
            pix = img.load()  # 转换为像素
            for x in range(img.size[0]):  # 处理上下黑边框，size[0]即图片长度
                pix[x, 0] = pix[x, img.size[1] - 1] = (255, 255, 255, 255)
            for y in range(img.size[1]):  # 处理左右黑边框，size[1]即图片高度
                pix[0, y] = pix[img.size[0] - 1, y] = (255, 255, 255, 255)
            if t is True:
                sentinel = 195
                for y in range(img.size[1]):  # 二值化处理
                    for x in range(img.size[0]):
                        # print(pix[x,y][0], pix[x,y][1], pix[x,y][2])
                        if pix[x, y][0] == 0 and pix[x, y][1] == 0:
                            pix[x, y] = (255, 255, 255, 255)
                        if pix[x, y][0] < sentinel or pix[x, y][1] < sentinel or pix[x, y][2] < sentinel:
                            pix[x, y] = (0, 0, 0, 255)
                        else:
                            pix[x, y] = (255, 255, 255, 255)
                img.save("new_get_image.jpg")  # 由于tesseract限制，这里必须存到本地文件
                text = pytesseract.image_to_string("new_get_image.jpg").replace(
                    '=', '').replace('S', '5').replace('l', '1').replace('s', '5')
                text = list(text)
                if len(text) != 0:
                    if text[1] == '4':
                        text[1] = '+'
                    elif text[1] == 'x':
                        text[1] = '*'
                    elif text[1] == '—':
                        text[1] = '-'
                text = eval(''.join(text))
            else:
                sentinel_ = 20
                sentinel = 140
                for y in range(img.size[1]):  # 二值化处理
                    for x in range(img.size[0]):
                        avg = int(sum([pix[x, y][0] , pix[x, y][1] , pix[x, y][2]]) / 3)
                        # print(pix[x,y][0], pix[x,y][1], pix[x,y][2])
                        if abs(pix[x, y][0] - avg) < sentinel_ and abs(pix[x, y][1] - avg) < sentinel_ and abs(pix[x, y][2] - avg) < sentinel_:
                            pix[x, y] = (255, 255, 255, 255)
                        if abs(pix[x, y][0] - pix[x, y][1]) > 50:
                            pix[x, y] = (0, 0, 0, 255)
                        if pix[x, y][0] < sentinel or pix[x, y][1] < sentinel or pix[x, y][2] < sentinel:
                            pix[x, y] = (0, 0, 0, 255)
                        else:
                            pix[x, y] = (255, 255, 255, 255)
                img.save("new_get_image.jpg")  # 由于tesseract限制，这里必须存到本地文件
                text = pytesseract.image_to_string("new_get_image.jpg").replace('.', '').replace(' ','')
            return text
        except Exception as e:
            return self.identification(url, headers, t)
identificationCodes = IdentificationCodes()
code = identificationCodes.identification()
print(code)