# 监控指定区间和指定时间范围内最低机票价格（美团网），并通过 SERVER 酱发送微信通知

import requests
import json
import pymysql
import time
from bs4 import BeautifulSoup
import datetime

# 连接数据库
conn = pymysql.connect(host='192.168.57.253', user='root', passwd='123456', charset='utf8')
cur = conn.cursor()
cur.execute('USE flight_price')

# 需要监控的航班信息
# id，起飞城市，到达城市，监控时间区间1，监控时间区间2，最低票价
cur.execute('SELECT * FROM moniting_data')
if cur.rowcount==0:
    exit()
flight_data = cur.fetchall()

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
session = requests.session()


# 从日历上获取最多30天内（含当天）的价格
def calender_price(dep_city_code, arr_city_code, start_date, end_date=None):
    # 把起始日期字符串转换为真正的日期以便比较日期大小
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # 结束日期可以不填，默认等于 start_date
    if end_date == None or end_date == '':
        end_date = start_date
    # 也要判断是不是日期格式，不是的话也需要转换
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # 如果时间间隔大于 29 天，那也只能使用 29 天
    if end_date > start_date + datetime.timedelta(29):
        end_date = start_date + datetime.timedelta(29)
    api_url = 'https://kuxun-i.meituan.com/getLowPriceCalendar/iphone/4/mt|m|m/' \
              '?startdate=' + str(start_date)[0:10] + \
              '&depart=' + dep_city_code + \
              '&arrive=' + arr_city_code
    api_data = session.get(api_url, headers=headers).content
    json_data = json.loads(api_data)
    date_price = json_data['data']['dataList']
    # 提取数据到新的 日期-价格 列表
    new_date_price = []
    for data in date_price:
        curr_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        if not ('price' in data.keys()):
            continue
        if curr_date < start_date or curr_date > end_date:
            continue
        new_date_price.append(data)
    return new_date_price


# 获取指定日期内的所有价格
# 如果日期间隔大于 30 天则需要多次使用 calender_prince 函数
def get_price(dep_city_code, arr_city_code, start_date, end_date=None):
    # 把起始日期字符串转换为真正的日期以便比较日期大小
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # 结束日期可以不填，默认等于 start_date
    if end_date == None or end_date == '':
        end_date = start_date
    # 也要判断是不是日期格式，不是的话也需要转换
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    # 获取 日期-价格 数据存储到列表
    date_price_list = []
    if start_date + datetime.timedelta(29) > end_date:
        for date_price in calender_price(dep_city_code, arr_city_code, start_date, end_date):
            date_price_list.append(date_price)
    else:
        curr_date = start_date
        while curr_date <= end_date + datetime.timedelta(29):
            for date_price in calender_price(dep_city_code, arr_city_code, curr_date,
                                             curr_date + datetime.timedelta(29)):
                date_price_list.append(date_price)
            curr_date = curr_date + datetime.timedelta(30)
    # 筛选掉不属于日期期间的数据
    # 上面为了防止出现curr_date大于end_date而部取数的情况，多加了一些天数
    new_date_price_list = []
    for data in date_price_list:
        curr_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        if curr_date < start_date or curr_date > end_date:
            continue
        new_date_price_list.append(data)
    return new_date_price_list


# 获取城市对应的三字码
def city_code(city_name):
    cur.execute('SELECT city_code FROM city_code WHERE city_name=%s', (city_name))
    return cur.fetchone()[0]


# 获取某一天的航班信息，并获取最低价格的航班信息
def flight_info(dep_city_code, arr_city_code, dep_date):
    api_url = 'https://kuxun-i.meituan.com/getflightwiththreecode/iphone/4/mt|m|m/' \
              '?depart=' + dep_city_code + \
              '&arrive=' + arr_city_code + \
              '&date=' + str(dep_date)[0:10]
    api_data = session.get(api_url, headers=headers).content
    json_data = json.loads(api_data)
    info = json_data['data'][0]
    # 航空公司，航班编号，起飞时间，到达时间，机票价格
    fli_info={'comp':'','flight':'','dep_time':'','arr_time':'','price':'',}
    #存储航班信息
    fli_info['comp']=info['coname']
    fli_info['flight'] = info['fn']
    fli_info['dep_time'] = info['s_time']
    fli_info['arr_time'] = info['a_time']
    fli_info['price'] = info['price']
    return fli_info


def send2wz(title,content):
    pass






cur.close()
conn.close()
