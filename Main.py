# 监控指定区间和指定时间范围内最低机票价格（美团网），并通过 SERVER 酱发送微信通知

import requests
import json
from bs4 import BeautifulSoup

# 需要监控的航班信息
# 起飞城市，到达城市，监控时间区间1，监控时间区间2，最低票价
flight_data = [
    ['杭州', '宜昌', '2017-10-07', '2017-10-08', ''],
]

# 请求头
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'kuxun-i.meituan.com',
    'Origin': 'http://i.meituan.com',
    'Referer': 'http://i.meituan.com',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
}

session=requests.session()
session=session.get('http://i.meituan.com',headers=headers)
t=session.cookies
print(t)


# 从日历上获取一个月内的最低价
def lowest_price(dep_city_code, arr_city_code, start_date):
    #api_url = 'https://api-m.kuxun.cn/getLowPriceCalendar/iphone/4/mt%7Cm%7Cm/' \
    #          '?depart=' + dep_city_code + \
    #          '&arrive=' + arr_city_code + \
    #          '&startdate=' + str(start_date)
    params={
        'startdate': str(start_date),
        'depart': dep_city_code,
        'arrive': arr_city_code
    }
    api_url = 'https://api-m.kuxun.cn/getLowPriceCalendar/iphone/4/mt%7Cm%7Cm/'
    api_data=requests.get(api_url,headers=headers,data=params).content
    json_data=json.loads(api_data)
    print(json_data)

def flight_info(from_city, to_city, fly_date):
    pass

#lowest_price('HGH','PEK','2017-10-01')
