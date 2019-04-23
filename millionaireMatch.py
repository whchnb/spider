import re
import os
import requests
import xlwt
import json
from w3lib.html import remove_tags

startt = 1
limit = 500
count = 500
url = 'https://www.millionairematch.com/search_results?w=gold_member&args_str=UmFuZG9tSVaTSo1D7eyHRpp54i1SjGNaikY7BnY8fbZDDzya4upDJgXc%2FzKGC%2FiTIXH37te8JZ5jsmbO0DAHimdU77RS1Uaf&search_part=&is_offset=1&last_results_order=&gallery_view=0&match_gender=1&is_distance=&passenger_type=&show_rule=&hst_id=113141460&haspicture=0&frompage=search_results&results_order=___by_log_time&remove_hidden=1&from={}&offset={}&count={}'.format(start, limit, count)
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'S_UUID=49490f3cff90e18f61c4ee32ec194a13f8775927; ms_ab_t=258504; _ga=GA1.2.1548616589.1555923322; _gid=GA1.2.693867308.1555923322; __auc=45b01dd916a44421f344b1aec36; BOSHSRV=b1; match_gender=1; gender=; ucd=nmm4e0f14838a460f3dcad84f94f4c467f9; testcookie=testcookie; GDSI=a40c08a67a63263e62c7fe53dc31c85c; S_UIDC=bcdc4b2cbeb1c77afca9c6a2e2d259a06ce316eb; username=ritchizhou11; password=NdUVLSm14C8WQiKm%2FmeChw; search_advanced_default=%7B%22checkbox%22%3A%7B%22match_marital%22%3A%5B%220%22%5D%2C%22relation%22%3A%5B%220%22%5D%2C%22match_ethnicity%22%3A%5B%220%22%5D%2C%22match_body%22%3A%5B%220%22%5D%2C%22match_religion%22%3A%5B%220%22%5D%2C%22match_education%22%3A%5B%220%22%5D%2C%22match_smoker%22%3A%5B%220%22%5D%2C%22match_drinker%22%3A%5B%220%22%5D%2C%22match_have_children%22%3A%5B%220%22%5D%7D%2C%22radio%22%3A%7B%22is_distance%22%3A%220%22%7D%2C%22select%22%3A%7B%22gender%22%3A%5B%222%22%5D%2C%22match_gender%22%3A%5B%221%22%5D%2C%22match_age_min%22%3A%5B%2220%22%5D%2C%22match_age_max%22%3A%5B%2259%22%5D%2C%22r_country%22%3A%5B%220%22%5D%2C%22match_r_state_id%22%3A%5B%22%22%5D%2C%22distance%22%3A%5B%22-1%22%5D%2C%22search_millionare%22%3A%5B%220%22%5D%2C%22search_photo%22%3A%5B%220%22%5D%2C%22match_height_min_all%22%3A%5B%224%22%5D%2C%22match_height_max_all%22%3A%5B%2234%22%5D%7D%2C%22text%22%3A%7B%22r_zip%22%3A%2210002%22%2C%22keywords%22%3A%22%22%2C%22save_search_criteria_name%22%3A%22Saved%20search%201%22%7D%7D; distance=-1; session_id=242610fd49df3dd0; _gat=1; mp_a2c7d3caa9e44466487cc47227770c58_mixpanel=%7B%22distinct_id%22%3A%20%2216a44421b3d1b8-0364b98e6af8fe-b781636-144000-16a44421b3e17e%22%2C%22%24device_id%22%3A%20%2216a44421b3d1b8-0364b98e6af8fe-b781636-144000-16a44421b3e17e%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; __asc=7c104b7416a4808f05a78902519',
    'Host': 'www.millionairematch.com',
    'Referer': 'https://www.millionairematch.com/search_results?args_str=UmFuZG9tSVYqHhKWgFtOeOBcVrvJEkCN0RA2MJKVMqW4u0R8zwvF68%2FTxYWpGhT%2FdrT3HVrXpDsRuPXRhNsg489%2BxzQNf7RJi3FhlyN5wTD96ytHjw9zGvnENfEKdP5Cd9ZNzM%2F54Ik2l0Hr%2FCnBjtmvVbaeknJauP0GmpGb1in%2FU6YeFHod5U7wQaRq9tEhkG8wUXeEdMsWtpjLBLGNX5wqhiX3DGLjeEMZwyfqs9Ut7gLyFDWHkGjInlPeEQbKfjvbdIDIIAM3mJ9a%2Bw0btotfl%2F%2FQKB8K&w=quick_search&count=500&store=&search_photo=0&is_distance=0&match_gender=1&hst_id=113114855&results_order=___original_order&offset=20',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}


def get_img(name, img_list):
    # 获取图片
    for index, url in enumerate(img_list):
        print('共{}张图片，正在下载第{}张'.format(len(img_list), index + 1))
        response = requests.get(url, headers=headers)
        with open('shejiao/{}/img/{}.jpg'.format(name, url.split('?t=')[1]), 'wb') as f:
            f.write(response.content)


def save_as_excel(name, datas, actives):
    # 保存至excel
    file = xlwt.Workbook(encoding='utf-8', style_compression=0)
    # 新建一个sheet
    profileSheet = file.add_sheet('profile', cell_overwrite_ok=True)
    profileSheet.col(0).width = 11111
    profileSheet.col(1).width = 11111
    profileSheet.col(2).width = 11111
    activeSheet = file.add_sheet('active', cell_overwrite_ok=True)
    activeSheet.col(0).width = 11111
    activeSheet.col(1).width = 11111
    line = 0
    for data in datas:
        # print(data)
        for index, d in enumerate(data):
            profileSheet.write(line, index, remove_tags(d))
        line += 1
    new_line = 0
    for active in actives:
        # activeSheet.write(new_line, index, )
        # print(active)
        if 'photo' in active[0].strip():
            activeSheet.write(new_line, 0, active[0].strip())
        else:
            activeSheet.write(new_line, 0, active[0].strip())
            activeSheet.write(new_line, 1, remove_tags(active[1].strip()))
        new_line += 1
    file.save('shejiao/{}/{}.xls'.format(name, name))


def save_as_json(name, data):
    # 保存至json文件
    data = json.dumps(data, indent='\n')
    with open('shejiao/{}/{}.json'.format(name, name), 'w') as f:
        f.write(data)


response = requests.get(url, headers=headers)
response = response.text
# print(response.text)
# with open('result.html', 'w', encoding='utf-8') as f:
#     f.write((response.text))
# response = open('result.html', encoding='utf-8').read()
user_info_re = re.compile(r'<a href="(.*?)" style="font-size: 15px; font-weight: bold;">')
user_info_url = re.findall(user_info_re, response) # 用户详情链接
# print(len(user_info_url))
err_url = []
err_dict = {}
err_count = 1
for page, url in enumerate(user_info_url):
    print(url)
    print('共{}条，正在获取第{}条'.format(len(user_info_url), page + 1))
    # url = 'https://www.millionairematch.com/user_details?prof_id=129804401&p=album&show_album_type=9'
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code == 200:
        try:
            response = response.text
            name_re = re.compile(r'<li>\s*?<h3>(.*?)</h3>', re.S)
            name = re.findall(name_re, response)[0].replace(' ', '_')
            age_gender_location_re = re.compile(
                r'<span><font id="age_orig_2">(.*?)</font>, <font id="gender_orig_2">(.*?)</font></span>.*?<span id="location_info">(.*?)</span>.*?Seeking\s(.*?)</span>',
                re.S)
            age, gender, location, see = re.findall(age_gender_location_re, response)[0]
            # print(age, gender, location, see)
            img_url_re = re.compile(r'"icon":"(.*?)"')
            img_url_link = re.findall(img_url_re, response)
            about_me_re = re.compile(
                # r'<div id=".*?" style="display: none; word-wrap: break-word;" .*?class="message_show_div">(.*?)</div>',
                r'<div id="about_me_orig" style="margin-top: 10px;">(.*?)</div>',
                re.S)
            about_me = remove_tags(re.findall(about_me_re, response)[-1])
            about_my_match_re = re.compile(r'<div id="match_about_orig" style="margin-top: 10px;">(.*?)</div>', re.S)
            about_my_match = remove_tags(list(re.findall(about_my_match_re, response))[0]).strip()
            my_questions_re = re.compile(r'<div id="my_questions_orig" style="margin-top: 10px;">(.*?)</div>', re.S)
            my_questions = re.findall(my_questions_re, response)[0].strip() if len(
                re.findall(my_questions_re, response)) != 0 else '-'
            three_tables_re = r'<tr id=".*?" class="item jq_edit_node">\s*?<td valign="top">\s*?' \
                              r'<span.*?>(.*?)</span>\s*?</td>\s*?<td valign="top">\s*?' \
                              r'<span id=".*?".*?>(.*?)</span>\s*?</td>\s*?<td valign="(?:top|bottom)">\s*?' \
                              r'(?:<span id=".*?" .*?>(.*?)</span>\s*?|\s*?)</td>\s*?</tr>'
            three_table_re = re.compile(three_tables_re, re.S)
            three_table = re.findall(three_table_re, response)
            two_table_re = r'<tr id=".*?" class="item jq_edit_node">\s*?' \
                           r'<td valign="top" width="30%">\s*?<span class="items">(.*?)</span>\s*?</td>\s*?' \
                           r'<td valign="top">\s*?<span id=".*?" >(.*?)</span>\s*?</td>\s*?</tr>'
            two_table_re = re.compile(two_table_re, re.S)
            two_table = re.findall(two_table_re, response.split('valign="bottom"')[1])
            actives_re = r'<span class="L_title">(.*?)</span>\s*?</div><p.*?>(.*?)</p>'
            active_re = re.compile(actives_re, re.S)
            actives = re.findall(active_re, response)
            with open('file.txt', 'w') as f:
                f.write(my_questions)
            ls = os.listdir('shejiao/')
            if name not in ls: # 不存在则创建文件夹
                os.mkdir('shejiao/{}'.format(name))
                os.mkdir('shejiao/{}/img'.format(name))
                print('创建成功')
            else:
                continue
            get_img(name, img_url_link)
            # datas = [
            #     ('url',url),
            #     ('name',name),
            #     # age, gender, location, see)
            #     ('age',age),
            #     ('gender',gender),
            #     ('location',location),
            #     ('see',see),
            #     ('about_me',about_me),
            #     ('about_my_match',about_my_match),
            #     ('my_questions',my_questions),
            #     ('----------','----------','----------'),
            #     ('Info', 'Me', 'Match')
            # ] + three_table + [('----------','----------','----------')] + two_table
            three_dic = {}
            for data in three_table:
                three_dic[data[0] + '_Me'] = data[1]
                three_dic[data[0] + '_My match'] = data[2]
            two_dic = {i[0]: i[1] for i in two_table}
            active_list = []
            for active in actives:
                # activeSheet.write(new_line, index, )
                # print(active)
                if 'photo' in active[0].strip():
                    active_list.append({active[0].strip(): '-'})
                else:
                    active_list.append({active[0].strip(): remove_tags(active[1].strip())})

            data = {
                'url': url,
                'name': name,
                'age': age,
                'gender': gender,
                'location': location,
                'see': see,
                'about_me': about_me,
                'about_my_match': about_my_match,
                'my_questions': my_questions,
                'Info': three_dic,
                'Others Info': two_dic,
                'active': active_list

            }
            print(data)
            save_as_json(name, data)
            # print(data)
            # save_as_excel(name, datas, actives)

        except Exception as e:
            err_dict[err_count] = {'url': url, 'err': e}
    else:
        print(response.status_code)
        err_url.append(url)

with open('err.txt', 'w+', encoding='utf-8') as err:
    err.write(str(err_dict))
    err.write(str(err_url))
err.close()
