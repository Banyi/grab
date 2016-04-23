#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import re
import requests
import http.cookiejar
from user import islogin
from bs4 import BeautifulSoup

req = requests.Session()
req.cookies = http.cookiejar.LWPCookieJar('cookies')
try:
    req.cookies.load(ignore_discard=True)
except:
    print(u'你尚未登录！')
    raise Exception(u'无权限（403）')
try:
    if islogin() == True:
        pass
except:
    print(u'身份已失效！')
    print(u'请运行user.py重新登录')
    raise Exception(u'无权限（403）')

class Question:
    soup = None
    def __init__(self, url, title=None): # 加URL检错
        if not re.compile(r'https://www.zhihu.com/question/\d{8}').match(url):
            raise ValueError("\"" + url + "\"" + ": 不是一个符合规定的url")
        else:
            self.url = url
        if title != None:
            self.title = title

    # 抓取网页
    def get_html(self):
        # r = requests.session()
        r = requests.get(self.url, cookies=req.cookies)
        self.soup = BeautifulSoup(r.content, 'lxml')

    # 获取标题
    def get_title(self):
        # 先判断实例中有无'title'属性
        if hasattr(self, 'title'):
            title = self.title
            return title
        else:
            if self.soup == None:
                self.get_html()
            soup = self.soup
            title = soup.find('h2', class_="zm-item-title zm-editable-content").get_text()
        return title

    # 相关话题
    def get_item_tag(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        item = []
        item_tag = soup.find_all('a', class_="zm-item-tag")
        for i in item_tag:
            item.append(i.get_text("", strip=True))
        return item

    # 话题描述
    def get_detail(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        detail = soup.find('div', id="zh-question-detail").get_text()
        return detail

    # 获取评论人数
    def get_comment(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        if soup.find('a', class_="toggle-comment meta-item") != None:
            comment_num = soup.find('a', class_="toggle-comment meta-item").get_text()
        return comment_num

    # 答案总数
    def get_answer_num(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        if soup.find('h3', id="zh-question-answer-num") != None:
            answer_num = soup.find('h3', id="zh-question-answer-num")['data-num']
        return int(answer_num)

    # 获取关注人数
    def get_follower(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        follower_num = soup.find('div', class_="zg-gray-normal").get_text()  # .strong.get_text()
        return follower_num

    # 回答
    def get_answers(self):
        answers_num = self.get_answer_num()
        if answers_num == 0:
            print(u'尚未有人回答该问题！')
            yield

        else:
            if self.soup == None:
                self.get_html()
            soup = self.soup

            answer = soup.find('div', class_="zm-editable-content clearfix").get_text()
            print('-----====***====--------')
            # for i in answer:
            print('answer_1: ', answer)

        return answer

    def get_top_i_answer(self, n):
        i = 0
        answers = self.get_answers()
        for answer in answers:
            i = i + 1
            if i > n:
                break
            yield answer
            print('answers: ', answer)