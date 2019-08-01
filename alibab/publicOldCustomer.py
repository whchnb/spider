# encoding: utf-8
"""
@author: Liwenhao
@e-mail: wh.chnb@gmail.com
@file: publicOldCustomer.py
@time: 2019/5/27 10:44
@desc:  公海客户信息获取
"""
from alibaba.oldCustomer import Customer


class PublicCustomer(Customer):

    # 继承父类 __init__ 方法
    def __init__(self, account):
        self.account = account
        self.count = 0
        self.name = self.__name()
        super(PublicCustomer, self).__init__(self.account)

    def __name(self):
        return '公海客户'


def main():
    # 账户
    account_list = [
        # 'fb2@jakcom.com',
        'fb3@jakcom.com',
        'tx@jakcom.com',
    ]
    # 公海客户目标url
    url = 'https://alicrm.alibaba.com/eggCrmQn/crm/customerQueryServiceI/queryPublicCustomerList.json?_tb_token_={}'
    for account in account_list:
        customer = Customer(account)
        # 获取所有国家
        country_list = customer.get_all_country()
        country_numbers = len(country_list)
        for index, country in enumerate(country_list):
            # 遍历每个国家，获取公海客户信息
            print('当前第个{}国家 共{}个'.format(index, country_numbers))
            try:
                status = customer.main(country, page=1, url_link=url)
                if status is False:
                    continue
            except Exception as e:
                customer.send_test_log(logName='alibaba 公海客户', logType='Error',msg='{} {} {}'.format(account, country['code'], str(e)))
                continue
        # 共获取的客户资料数量
        print(customer.count)


if __name__ == '__main__':
    main()