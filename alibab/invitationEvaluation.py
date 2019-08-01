# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: invitationEvaluation.py
@time: 2019/6/18 17:44
@desc:  订单评价
"""
import urllib3
import requests
from urllib.parse import urlencode
from alibaba.public import Public


urllib3.disable_warnings()


class InvitationEvaluation(Public):
    def __init__(self, account):
        self.account = account
        super(InvitationEvaluation, self).__init__(self.account)

    # 发送信息
    def send_message(self, orderId):
        ctoken = self.get_ctoken()
        url = 'https://fb.alibaba.com/review/action/inviteReviewAction.do?'
        params = {
            'reviewEntity': 'TAOrder',
            'entityId': orderId,
            'ctoken':ctoken
        }
        url = url + urlencode(params)
        data = {
            '_tb_token_': self.tb_token,
            'inviteComment': 'Dear friends, thank you very much for your order, we are looking forward to get a long-term cooperation with you;\nAny problems and suggestions about the products or services, please contact with us ,we will try best to make positive corrections;\nFinally, please takes some free time to give an feedback with 5-star, this will be a driving force for us to work hard, thank you again'
        }
        headers = {
            'authority': 'fb.alibaba.com',
            'path': '/review/action/inviteReviewAction.do?reviewEntity=TAOrder&entityId=%d&ctoken=%s' % (orderId, ctoken),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': self.cookie,
            'origin': 'https://fb.alibaba.com',
            'referer': 'https://fb.alibaba.com/review/reviewList.htm?tradelog=from_orderlist_menu&currentPage=4',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        response = requests.post(url, data=data, headers=headers, verify=False)
        status = response.json()['code']
        print(response.json())
        if status == 200:
            return 'success'
        else:
            return response.json()

    def main(self, orderId):
        msg = self.send_message(orderId)
        return msg


def main():
    orderId = 12967559001027929
    invitationEvaluation = InvitationEvaluation('fb2@jakcom.com')
    invitationEvaluation.main(orderId)


if __name__ == '__main__':
    main()

    '''
    ali_apache_id=11.179.217.87.1557109662927.980741.2; t=0ec389e5303cc4ad299e6c6d2807925d; cna=n4lWFZbRW2YCAbe/sh4Lxj33; gangesweb-buckettest=183.191.178.30.1557109697018.0; UM_distinctid=16a8af9c7e322e-0f2c1ced40471a-e323069-15f900-16a8af9c7e4432; _ga=GA1.2.1933742769.1557196023; _m_h5_tk=51c11293b3f29f0c165763e0926705db_1560424966037; _m_h5_tk_enc=0e2e1014ea6809739226ffdf5197bbf7; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1560769958437&x_user=CN|Ady|Cao|cgs|229737297&no_popup_today=n; sc_g_cfg_f=sc_b_locale=en_US; acs_usuc_t=acs_rt=e1d1ba33c2874ecf9ec021cbca1082ea; cookie2=15adacdc6bbffd264a920f6c35e9200f; _tb_token_=e5b534d50a556; intl_locale=zh_CN; ali_apache_tracktmp=W_signed=Y; _hvn_login=4; csg=d2761043; xman_us_t=ctoken=obh47elr_snu&l_source=alibaba&x_user=5EOZ4PH61D/gZ7kFsNP43QfdvP1npNBDfmGT6pisBwg=&x_lid=jakcomtech&sign=y&need_popup=y; intl_common_forever=Uqhdm5b55qrpmr60gvWv5La+hreNRjNz0nsc8Ti4HsVsDi+uMBs8KA==; xman_f=hY8nuTevn7RKr0GizxKZ5MII8mV1aHYJpeLybhVs1c5XhP+uowmrRg4pBI4KPLBXwKZCNmNa6F8pVJvXkGRUYT4PsPKEEdJOuS+i35u7/QNV1bjHrtdhRcH0df2uUBnDmbFvDt8QILgQuZTk70gnXiZNfMRGxnVS3AGzQLHbeQebxd33W6SgagydLtlb8En9ynu3PLC1/+8MxPX73NFHbv0zk0WMtFt5JNJ+Hj1983dmSElXXtqMs+fl2JOcM+agvlu5Ew54QhTTeP70NBhTVedC02efd/GJitpRBTCu0BTFJa0JjLU3dBzuZNQZikBf1Wyk7VdpKo9yXvkUW5D4zN7mqGymIIz755YowyU/fokTGh9rNDZLxm7W49e1IrWF; l=bBQ0s6OIvqLqga9LBOfNquI8LS7OPIRf1sPzw4OgiICPOf1y53sdWZh99rY2C3GVa6iMy35fHFhvB5TUZyznh; ali_apache_track=ms=|mt=3|mid=jakcomtech; xman_t=BICh6m7eBAFPHNFfnfZKktIcatwdiRIIXXkapcAAVvd3dIdYbELKnlTj4PbS1SGRvQM5kVUTDur+vqQpk08COk1xVEu0B7WSbmAvLJ3eUV9KseTlFw+D8d9wiu7iORAmRN1g+8O85KiOL2DxiqxkkP3T0IYr668ylDMUk8pzXLS4TtYT1Fqmwt+f5ysDPPpUDQZqm5LSzuv5V67dDXIGy95ZnYOpjc0BppevJp6T9twyghsEtAgs5rLJvFSQsAlfqt3mCsQx2vWswcQb2rRmEqdOuBl6IiB9CrUBJp6eNK9xpxcgPw4m7vx5d4k826got36+FpsZZNJh8F9x1Z3x7vZw/aNGsIb4ZLvOL1q5maQbc7lHpR6sgw8jPSVLTEz04G/fxCJPkGFvAPqJOLMg81OPXMAiHQxOOBUl6+VeBUWSuZH6KRAoWlCO7W53CRkC7ytPW3BGvd0ROy6Dl5GLfgjUChFrIlHsIfRd5UbDX8gS755Xo99G/v39D3x1FfkbAozGulZCUDCPBBI01FDwXKyj4veYdKAmwDvdL5fhR/U76Hqjhn3YvFIw3PNLYzvxun1srW2w6bJ+esqEnU3IaKUxqn9apvBIuNZV2tPtjEKRaZTrEpc3AQYBtttNxPpulmz6IOPiLzfMiVMXBssF7RMxJUv+2KRHzjDDHmL2sT9lwAls9IBFwQ==; isg=AtTUg3tFdY8mJOA32_tslseNpRKGhfmXxkBbtG63yN_xWXejlDmApaabL2e9
    https://fb.alibaba.com/review/action/inviteReviewAction.do?reviewEntity=TAOrder&entityId=13739626501024644&ctoken=obh47elr_snu
    https://fb.alibaba.com/review/action/inviteReviewAction.do?reviewEntity=TAOrder&entityId=13721867001029936&ctoken=obh47elr_snu
    '''
