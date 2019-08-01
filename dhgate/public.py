# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: public.py
@time: 2019/7/20 19:18
@desc:
"""
import re
import json
import requests
from http import cookiejar
from urllib.parse import urlencode


class Main:
    def getAcoountPwd(self):
        url = 'http://py1.jakcom.it:5000/dhgate/get/account/all'
        response = requests.get(url)
        accoPwd = sorted({i[0]: i[1] for i in eval(response.text)}, key=lambda x: [x[x.index(i)] for i in x])
        # print(accoPwd)
        return accoPwd

    def bug(self, logName, logType, msg, position='敦煌'):
        msg = str(msg)
        test_url = 'http://192.168.1.160:90/Log/Write'
        data = {
            'LogName': logName,
            'LogType': logType,
            'Position': position,
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': msg,
        }
        test_response = requests.post(test_url, data=data)
        print('test_response', test_response.text)


class Public:
    def __init__(self, account):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'Cookie': '_Jo0OQK=56FCFAA5439F379A64739C4E6210F7B3B7FC285756F66EC99D2D94592E9AD6C8D6BC0A4DC8E099651873E32E20E3E0B0E52A64203F72646754947FEA54EFB299CDD5FD42A43077F8B35310090C00A666A29310090C00A666A297C59BADD6A74849CGJ1Z1cA==;JSESSIONID=71662160EF640D7833614CE3E6F3ABB8;dhpath_c=null;CASTGC=TGT-300049-YzO07pDJWg1UkvIrwj6YLoK7h7mHbpDfbkezSoQNvwCeO5pqjz-passport.dhgate.com;JSESSIONID=C9E33282CD0206D3F2E41E7300D72C34;_Jo0OQK=4847DF17E6ED079B6E01DD7798B31E830AC9A57CAE6D2CFA4B0A84B4D131F4068477EF9B5420B01C7FDA62967E164AD38AF5E5F45D95B73991B691515E8F303988C17E3532685D6D7737DEE37C821ABA63C7DEE37C821ABA63C5B9A77E88AB369BDGJ1Z1Vw==;c_sessionid=b6299966-7006-4b1b-a9c9-20e313998e30;page_image=9041;dhc_s=43fa7b12-93ed-4f06-8296-4d9008dea6cb;dh_s_t=5122751455de8ef4c7e3f7d3fee0d9e876b4358450d5c2c89ec2ee5aaf87cfec405483dbd9d6e0e12e99c02747b28b4c595421b6142bb911db822580436b42bd62673f4f7b53b38b87baebea1d84f12926b117ee407cac77fd7098f367473f820e451b03844492e9a8e7c4d1cc2faa8ef0fd10411ef6a13fb9496921ad1a20e525e2bca8eb6402a8d29593d28bd4f491;_s_o0l=f5a6e997f22ce63c1d6abd3dc4c7c4554c1af88c5df3b27981cf080675834037;username=k6tech1;supplierid=ff80808151d94d9d0152df60d835654b;T_status=1;_Session_ID=X7jyGViJVnQw5SyW3MTrL9jG6kcvQ8iWONljY6Vx;php_qa_sellerKey=LonPBgoTGAH62f4VuXFGI2ZWRsya4MDUjnDRcG2l;seller_new_lv=0;',
            'Host': 'seller.dhgate.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }
        self.account = account
        # self.getAcoountPwd()
        self.getCookie()

    def getAcoountPwd(self):
        url = 'http://py1.jakcom.it:5000/dhgate/get/account/all'
        response = requests.get(url)
        accoPwd = sorted({i[0]: i[1] for i in eval(response.text)}, key=lambda x: [x[x.index(i)] for i in x])
        print(accoPwd)
        return accoPwd

    def getCookie(self):
        url = 'http://cs1.jakcom.it/DH_interface/dhgate_login?account=' + self.account
        response = requests.get(url)
        self.cookie = response.text[1:-1]
        # print(self.cookie)
        self.cookie = 'vnum=219;lastvisittime=1564284847841;php_qa_sellerKey=ev32DkeNBMNH8tnTi2DXVDzpaKcMp1tBXe7dDKvJ;_Session_ID=SYYwxJhp41HOzZnNpHu1RLDJV6A6sUOg41DmO1vq;username=k6tech10;dh_s_t=c268ffe26256d4efe571346515a05ab5935b2e107efe8233b0095e7c65f0153c43eaa4fad90cc4ed7e799df475782db2a67cd4863963c6c2dd66431d6ee9cc882dcc9f79fb16013b1143e967f142bf095849106d1b1fead48fcef2d3b6e614bd6924d4a26f8a4649af78084d8b8d50b4976dd0d0c0fe6649b4d4b025044bdedb4658ee746def23448b98fe394b0925ce5657b5d7085f7063;page_image=9041;dhc_ol=1564284843405;seller_site_region=CN;JSESSIONID=4AC2036A86CA4119A35D55B4C5098964;__utmt=1;dhpath_c=null;dht_lot=Public_S0003;session=VNqxoRGxMKeez75-n2ZHxw;_Jo0OQK=425704E91149FD8A3EAC6DC246E9E071D9C0D2D2EF7DC854178B2B0051282BB70D03EEC496431DE50D7A7A9683CF371B8EA3B017851E48D4DD407B9DAF62E4DC8077D0AC832322BD2DD310090C00A666A29310090C00A666A297C59BADD6A74849CGJ1Z1dA==;supplierid=ff808081533bfd42015389872cd1025b;cookie_noticeid=9ae30950-3889-4abc-bfbc-10f2635dca98;seller_new_lv=0;seller_site_lang=zh_CN;__utmb=251624089.133.10.1564276901;menu_2_closes=;T_status=1;__utmc=251624089;__utma=251624089.109497977.1564052003.1564204973.1564276901.3;dh_syi_l_v=1;__utmz=251624089.1564052003.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none);LASTUPP=ff8080816bf4555e016c369e76e40b7a;_s_o0l=030933e4b7dc1956612a477b9e5d69ab0b0b7639fd5a16885c5ba27e9fdae190;com.dhgate.apsaras.internation.CookieLocaleResolver.LOCALE=zh_CN;pvn=233;c_sessionid=a5ef42c9-05f5-4073-bdba-3670b85849b5;dhc_s=5595faa9-5c93-49b8-9895-c11009b9c392'
        self.headers['Cookie'] = self.cookie

    def send_test_log(self, logName,logType, msg, position='0'):
        msg = str(msg)
        test_url = 'http://192.168.1.160:90/Log/Write'
        data = {
            'LogName': logName,
            'LogType': logType,
            'Position': position,
            'CodeType': 'Python',
            'Author': '李文浩',
            'msg': msg,
        }
        test_response = requests.post(test_url, data=data)
        print('test_response', test_response.text)

    def main(self):
        pass
        # self.setCookieStep2()


def main():
    public = Public('jakcomdh')
    public.main()


if __name__ == '__main__':
    main()
