#!/user/bin/env python3
# _*_ coding: utf-8 _*_


import re
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
soup = BeautifulSoup(r.content, 'lxml')
title = soup.title.get_text()
# print('title: ', title)

# 相关话题
item_tag = soup.find_all('a', class_="zm-item-tag")
item = []
for i in item_tag:
    item.append(i.get_text(" ", strip=True))
# print(item)

# 问题描述
question_detail = soup.find('div', id='zh-question-detail').get_text()

# 评论人数
comment = soup.find('a', class_="toggle-comment meta-item").get_text()
# print('comment:', comment)

# 抓取关注人数
question_followers = soup.find('div', class_="zg-gray-normal").a
print('question_followers: ', question_followers)     # None

# 回答人数
answers_num = soup.find('div', class_="zh-answers-title clearfix").h3.get_text()
print('answers_num:', answers_num)

# 赞同数
vote_count = soup.find('button', class_="up").span.get_text()
print('up_count: ', vote_count)

# 回答者
author = soup.find('a', class_="author-link").get_text()
print('author: ', author)

# 答案发布时间
answer_data = soup.find('a', class_="answer-date-link meta-item").get_text()
print(answer_data)
# 答案
answer = soup.find('div', class_="zm-editable-content clearfix").get_text()
# print(answer)