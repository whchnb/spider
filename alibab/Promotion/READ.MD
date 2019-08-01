### 阿里巴巴访客营销

###### 项目工程目录如下

```阿里巴巴访客营销
.
+--- Promotion
|   +--- alibabaMarket.py
|   +--- timing.py
|   +--- ua.txt
|   +--- market.log
```


###### 文件说明
*alibaba_market.py*

	alibabaMarket.py 为该项目主文件，通过构造请求来达到自动营销的目的
	
*timing.py*

	timing.py 为定时脚本，使alibabaMarket.py在每天的01:00定时进行营销任务

*ua.txt*

	ua.txt 为存储ua文件，ua在最后一步进行营销请求时使用，同一个ua 短时间无法重复使用，否则会出现601错误
	
*market.log*

	market.log 为日志文件，包含有任务日志状态，cookie状态，营销状态
	
