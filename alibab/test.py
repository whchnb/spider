import requests

url = 'http://cs1.jakcom.it/AlibabaProductManage/servicedata'
res = requests.get(url)
print(res.text)