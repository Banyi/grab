#!/user/bin/env python3
# _*_ coding: utf-8 _*_

'''
1.BeautifulSoup4解析html
2.requests库,抓取页面
3.class Question,问题
4.class Answer
5.加载cookie查看登录状态，判断知乎是否登录，
  调用islogin(),如果登录成功则继续，若失败则返回登录执行user.py
'''

import requests
import http.cookiejar
from user import Logging, islogin
from bs4 import BeautifulSoup

req = requests.Session()
req.cookies = http.cookiejar.LWPCookieJar('cookies')
try:
    req.cookies.load(ignore_discard=False)
except:
    Logging.error(u'你尚未登录！')
    Logging.info(u'')
    raise Exception(u'无权限（403）')

try:
    if islogin() == True:
        pass
except:
    Logging.error(u'身份已失效！')
    Logging.info(u'请运行user.py重新登录')
    raise Exception(u'无权限（403）')

url = "https://www.zhihu.com/question/42180532"
r = requests.get(url)
# print('status_code: ', int(r.status_code))
soup = BeautifulSoup(r.content, 'lxml')
# print(soup.prettify())
title = soup.title
item_tag = soup.find_all('a', class_="zm-item-tag")
print('item_tag: ', item_tag)