# 监控指定区间和指定时间范围内最低机票价格，并通过 SERVER 酱发送微信通知

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# 需要监控的航班信息
# 起飞城市，到达城市，监控时间区间1，监控时间区间2，最低票价
flight_data = [
    ['杭州', '宜昌', '2017-10-07', '2017-10-08', ''],
]

# 请求头，好像没什么用
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

# 开启 PhantomJS
driver = webdriver.PhantomJS()


def flight_info(from_city, to_city, fly_date):
    web_url = 'https://sjipiao.fliggy.com/flight_search_result.htm'
    driver.get(web_url)
    # 出发城市
    dep_city = driver.find_element_by_name('depCityName')
    dep_city.clear()
    dep_city.send_keys(from_city)
    city_click = driver.find_element_by_class_name('J_ResultsList')
    city_click.click()
    # 到达城市
    arr_city = driver.find_element_by_name('arrCityName')
    arr_city.clear()
    arr_city.send_keys(to_city)
    city_click = driver.find_element_by_class_name('J_ResultsList')
    city_click.click()
    # 出发日期
    dep_date = driver.find_element_by_name('depDate')
    dep_date.clear()
    dep_date.send_keys(str(fly_date))
    # 回车开始搜索
    dep_date.send_keys(Keys.RETURN)
    # 解析网页
    web_html = driver.page_source
    bs_obj = BeautifulSoup(web_html, 'html.parser')
    print(bs_obj)
    driver.close()


flight_info('杭州', '宜昌', '2017-10-11')
