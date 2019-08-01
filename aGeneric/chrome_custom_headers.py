old_headers = """:authority: post.alibaba.com
:method: POST
:path: /product/asyncOpt.htm?optType=productRiskCheckAsyncRender
:scheme: https
accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7
awsc-token: TA4A2D29E08C5C68C4F46023A267E331F26F38AF6509A520D23E13B1D0F
awsc-token-type: pc
content-length: 60775
content-type: application/x-www-form-urlencoded
cookie: x-gpf-render-trace-id=0bb3d94915644633803635103e5219; ali_apache_id=11.179.217.160.1564272576880.515862.7; t=d4463e8295c234a85a725398a84dd3bf; cna=BwfDFZ114xECAbe5i4kV/VDQ; last_ltc_icbu_icbu=cHdk; gangesweb-buckettest=183.185.139.137.1564272584922.1; _bl_uid=kOjUdybdm08lj58903UC1b3o4w1k; acs_usuc_t=acs_rt=dc8a3bc8e4ac44babc5f1cbd5b07e9f3; cookie2=1764e06e30060cc56ae50b6158e40774; _tb_token_=ee57beb6116e9; intl_locale=zh_CN; ali_apache_tracktmp=W_signed=Y; xman_us_f=x_locale=zh_CN&x_l=1&last_popup_time=1564272582164&x_user=CN|Ady|Jakcom|cgs|230822478&no_popup_today=n; XSRF-TOKEN=e3e9e9cc-dffb-4f74-a51b-6757f4b49eba; _hvn_login=4; csg=bb6d6f7d; xman_us_t=ctoken=ex2cyw4e6_yu&l_source=alibaba&x_user=AEd5oz7VBwCxSNUT6pMbo2baIr80f8am8bUyO5NU1W4=&x_lid=jakcomb2b&sign=y&need_popup=y; intl_common_forever=8gL+6IawcUQWZLGB5JitbkncqS+3KqeRoP/JnKI2t+mWjb7LQGxRqg==; xman_f=MuV80zmwdwefuaJIFZtp8emSOTI4P4bTmgON6mNdWaiEGPN7bjKaC55suQE4c9D/9CBb7FQeVp2yM4f7FezrI2VNfRUqRtqhPTGHtGJ1rYKwqdtvFAnPXvkr9VCX4ornwTcOut88vMYHOgjn4CFLYmksX3Za6WpCBYinLllK3CfIou8KT45LhqWT3wee/Y2lQKxtAiuSRfroQxKq3Ryi3mMM/tiCD7Z/pwhvKn2bxI55HntKrsJkc2Fx+ohKGBLgzBkzNQzePcNSYjDpsN+booLeicbGCalnHPF9IZCslKYv3lEcI/hlrKLH+Or/ntDGXT0LlEc7bb7ByQPaRQQF9YvR9YKtsr+B4gXOTD9iMEACDRr2u/BTScBYvXmaB3UX; ali_apache_track=ms=|mt=3|mid=jakcomb2b; JSESSIONID=927FC1049FC38034C9EE45D24F1E7D2B; xman_t=KFRtE90g2YNqlx4IKvAV4laGv3/XmmUK2Um4bL+J8WNVkChRCnVL8Au9VwKxAofRqW2ohJaID8oZuAgrxXm1uBqd2vskVwEnRZI5PEhh1uo89Zk8Y/vOvhUn+Tz2tJq1D5SslsdUcKIclFnA0zEYNdCk0/LZsVXlDQaXBRH+jggY/mfb0pNJ76Vn/fheTVozjjxrXSNX1gaQpQpwc7XodUJrBC0lzcsEzxWdCLfkMkkNZjIsW913tXa5meLpoBASUU9x6tIbdv2xHBL2Ww4brOm6jvTRNtaTYuWCe55AmJEb++OlpvQ3NXvVdpoRjGGMa7pzXyA1SvlY7OpWIempEROxmxrRkfxQBhyBfwJa0izFZNkS43rzt1Zi7xF6nN8oNSgH5MJt+gsMrNBLRKbp4W9jHNWHdeH+hGh1UAv1GDPIgJDvfrtLiRH7y/e2Mh4AdDjwQaLzQ7QiDHugEYTLahqgVnRHGYqENuuoksU6UuStD/epNcYySj8X6g5rOWIq1V38VpBiGkLJCMqcuwaMT0cWZfFtJs6odhslgDNkKMKr5kHPUcyErpgITbhrk5IPze+U1QBPqybpOLAMUQSGgcx6B+C8V2remfYuBGU4HWPh5/CwLKIVbMWqKyVbClw0EgQ4gn4IU9x3qbdEBhK6O+WtTODbhyeEoUERZu4UezyfJjPZ0kZx7zfi1v7FO4VN; l=cBMjE6klqINTpo5UBOfwVuI8LS79PIdfCsPzw4OgiICP_26WIKbhWZ3HYwxXCnGVLsUkR3rCLlQLBVLSHPathL0Zp0i_KHGl.; isg=BHd3An7T5nHEcmL-Xpd6nEwiBmsBlEoeNeOIicklN8aVeJG60Qic7EMeXpiDkCMW
origin: https://post.alibaba.com
referer: https://post.alibaba.com/product/publish.htm?itemId=60761180712
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36
x-requested-with: XMLHttpRequest
x-xsrf-token: e3e9e9cc-dffb-4f74-a51b-6757f4b49eba"""

headers = old_headers.split('\n')
for i in headers:
    print("'{}': '{}',".format(i.split(': ')[0].strip(), i.split(': ')[1].strip()))
