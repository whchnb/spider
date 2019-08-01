a = """orderId = data['payload']['orderInfo']['orderId']   # 订单号
                orderUrl = data['payload']['orderInfo']['orderUrl']   # 订单详情链接
                reviewTime = data['payload']['orderInfo']['reviewTime']   # 更新时间
                buyerName = data['payload']['orderInfo']['buyerInfo']['name']   # 买家姓名
                buyerCountry = data['payload']['orderInfo']['buyerInfo']['countryName']   # 买家国家
                buyerCountryCode = data['payload']['orderInfo']['buyerInfo']['countryCode']   # 买家国家缩写
                supplierServicesStars = data['payload']['supplerReview']['latitudeScoreList'][0]['score'] # 供应商服务星级
                supplierServicesDescription = self.star[int(supplierServicesStars)]   # 供应商服务描述
                shippingTimeStars = data['payload']['supplerReview']['latitudeScoreList'][1]['score'] # 按时发货星级
                shippingTimeDescription = self.star[int(shippingTimeStars)]   # 按时发货描述
                orderStars = data['payload']['productReview'][0]['latitudeScore']['score']  # 订单评价星级
                orderDescription = self.star[int(orderStars)]   # 订单评价描述
                productId = data['payload']['productReview'][0]['productId']    # 产品id
                productUrl = data['payload']['productReview'][0].get('productUrl', '已下架')    # 产品链接
                productTitle = data['payload']['productReview'][0]['productName']    # 产品标题
                productImageUrl = data['payload']['productReview'][0]['productImageUrl']    # 产品图片
                reviewId = data['payload']['productReview'][0]['reviewId']    # 评价Id
                reviewContent = data['payload']['productReview'][0]['reviewContent']    # 评价内容
                replyName, replyTime, replyContent = '-', '-', '-'
                    replyName = data['payload']['productReview'][0]['replyName']    # 回复人
                    replyTime = data['payload']['productReview'][0]['replyTime']    # 回复时间
                    replyContent = data['payload']['productReview'][0]['replyContent']    # 回复内容"""

b = ''
for i in a.split('\n'):
    b = b + '"' + i.split('=')[0].strip() + '": "' + i.split('#')[-1].strip() + '", '
print(b)