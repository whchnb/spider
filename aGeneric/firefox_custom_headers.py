old_headers = """event	fetchList
status	all
gmtCreate	;
linkedCount	;
page	1
pageSize	10
canUpgrade	;
subject	B3主图
quality	;
maxFileSize	;
minFileSize  ;"""
a = old_headers.split('\n')
for i in range(0, len(a), 2):
    print('"{}": "{}",'.format(a[i].strip(), a[i+1].strip()))