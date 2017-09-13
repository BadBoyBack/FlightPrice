# 监控指定区间和指定时间范围内最低机票价格（美团网），并通过 SERVER 酱发送微信通知

import requests
import json
import pymysql
import datetime
import time

# 连接数据库
conn = pymysql.connect(host='192.168.57.253', user='root', passwd='123456', charset='utf8')
cur = conn.cursor()
cur.execute('USE flight_price')

# 需要监控的航班信息
# id，起飞城市，到达城市，监控时间区间1，监控时间区间2，最低票价
cur.execute('SELECT * FROM moniting_data')
if cur.rowcount == 0:
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


# curr_date 转换之后会变成 datetime.datetime 无法与 datetime.date 比较，所以需要增加这么一步
def date_trans(trans_date):
    if isinstance(trans_date, datetime.datetime):
        trans_date_str = str(trans_date)
        str_year, str_mon, str_day = int(trans_date_str[0:4]), int(trans_date_str[5:7]), int(trans_date_str[8:10])
        transed_date = datetime.date(str_year, str_mon, str_day)
        return transed_date
    else:
        return trans_date


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
    start_date = date_trans(start_date)
    end_date = date_trans(end_date)
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
        curr_date = datetime.datetime.strptime(str(data['date'][:10]), '%Y-%m-%d')
        curr_date = date_trans(curr_date)
        if not ('price' in data.keys()):
            continue
        if curr_date < start_date or curr_date > end_date:
            continue
            datetime.date.strftime()
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
    start_date = date_trans(start_date)
    end_date = date_trans(end_date)
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
            curr_date = date_trans(curr_date)
    # 筛选掉不属于日期期间的数据
    # 上面为了防止出现curr_date大于end_date而部取数的情况，多加了一些天数
    new_date_price_list = []
    for data in date_price_list:
        curr_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        curr_date = date_trans(curr_date)
        if curr_date < start_date or curr_date > end_date:
            continue
        new_date_price_list.append(data)
    return new_date_price_list


# 获取最低价格对应的日期（可能不止一个）
def lowest_date(date_price):
    # if len(date_price) == 1:
    #     return date_price[0]['date']
    date_index = 0
    for data in date_price:
        if int(data['price']) < int(date_price[date_index]['price']):
            date_index = date_price.index(data)
    # 可能会存在多个最低价的情况，所以需要分别存储
    lowest_date_list = []
    for data in date_price:
        if data['price'] == date_price[date_index]['price']:
            lowest_date_list.append(data['date'])
    return lowest_date_list


# 获取城市对应的三字码
def city_code(city_name):
    cur.execute('SELECT city_code FROM city_code WHERE city_name= %s', (city_name))
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
    # 航空公司，航班编号，起飞日期，起飞时间，到达时间，机票价格
    fli_info = {'comp': '', 'flight': '', 'date': '', 'dep_time': '', 'arr_time': '', 'price': '', }
    # 存储航班信息
    fli_info['comp'] = info['coname']
    fli_info['flight'] = info['fn']
    fli_info['date'] = str(dep_date)[0:10]
    fli_info['dep_time'] = info['s_time']
    fli_info['arr_time'] = info['a_time']
    fli_info['price'] = info['price']
    return fli_info


# 发送微信群通知
def send2wx(title, content):
    sendkey = ''
    sc_url = 'https://pushbear.ftqq.com/sub?sendkey=' + sendkey + '&text=' + title + '&desp=' + content
    requests.post(sc_url)


# 主程序
for monitor in flight_data:
    curr_id, dep_name, arr_name, start, end, price = monitor
    dep_code = city_code(dep_name)
    arr_code = city_code(arr_name)
    all_date_prices = get_price(dep_code, arr_code, start, end)
    lowestdates = lowest_date(all_date_prices)
    for lowestdate in lowestdates:
        try:
            fli_info = flight_info(dep_code, arr_code, lowestdate)
        except:
            continue
        # 对比存储在数据库中的价格，如果低于则继续运行程序并存储这个价格
        if int(fli_info['price']) > 0 and int(fli_info['price']) < int(price):
            cur.execute('UPDATE moniting_data SET Price=%s WHERE id=%s', (int(fli_info['price']), curr_id))
            conn.commit()
        else:
            continue
        send_title = '发现' + dep_name + '到' + arr_name + '的历史最低价'
        send_content = '航空公司：' + fli_info['comp'] + \
                       '\n\n航班编号：' + fli_info['flight'] + \
                       '\n\n日期：' + fli_info['date'] + \
                       '\n\n时间：' + fli_info['dep_time'] + \
                       ' -' + fli_info['arr_time'] + \
                       '\n\n价格：' + str(fli_info['price']) + '元'
        send2wx(send_title, send_content)
        # 为了防止获取不到数据，需要先暂停一段时间
        time.sleep(30)

# 关闭数据库连接
cur.close()
conn.close()
