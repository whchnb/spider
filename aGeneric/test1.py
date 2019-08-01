import re
import json
import requests
import datetime
from urllib.parse import parse_qs

url = "http://py1.jakcom.it:5000/alibaba/post/info/item_post_data"
data = {
    "item_id": 62226669869
}
response = requests.post(url, data=data)
datas = parse_qs(eval(response.text)[0][4])
print(datas['jsonBody'][0])
# data = datas[0][4][44:]
# # print(data[44:])
# # print(unquote(data).replace('+', ' '))
# print(json.loads(unquote(data).replace('+', ' ')))
# jsonBody = json.loads(datas['jsonBody'][0])
# print(datas['jsonBody'][0])
