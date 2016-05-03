#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import re
import os
import requests
from bs4 import BeautifulSoup


session = requests.Session()

'''
session.cookies = http.cookiejar.LWPCookieJar('cookies')
# print('cookies: ', req.cookies)

try:
    session.cookies.load(ignore_discard=True)
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
'''


class Question:
    soup = None
    url = None
    def __init__(self, url, title=None):
        if not re.compile(r'https://www.zhihu.com/question/\d{8}').match(url):
            raise ValueError("\"" + url + "\"" + ": 不是一个符合规定的url")
        else:
            self.url = url
        if title != None:
            self.title = title


    def get_html(self):
        r = session.get(self.url)    # cookies=session.cookies
        self.soup = BeautifulSoup(r.content, 'lxml')

    def get_title(self):
        if hasattr(self, 'title'):
            title = self.title
            return title
        else:
            if self.soup == None:
                self.get_html()
            # soup = self.soup
            title = self.soup.find('div', id="zh-question-title").h2.string
        return title

    def get_topics(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        item = []
        item_tag = soup.find_all('a', class_="zm-item-tag")
        for i in item_tag:
            item.append(i.get_text('', strip=True))
        return item

    def get_detail(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        detail = soup.find('div', class_="zm-editable-content")
        if detail != None:
            return detail.get_text()

    def get_comment(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        if soup.find('a', class_="toggle-comment meta-item") != None:
            comment_num = soup.find('a', class_="toggle-comment meta-item").get_text()
        return comment_num

    def get_answer_num(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        if soup.find('h3', id="zh-question-answer-num") != None:
            answer_num = soup.find('h3', id="zh-question-answer-num")['data-num']
        return int(answer_num)

    def get_follower(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        follower_num = soup.find('div', class_="zg-gray-normal")  # a.strong.string
        return follower_num

    def get_all_answers(self):
        answers_num = self.get_answer_num()
        if answers_num == 0:
            print(u'尚未有人回答该问题！')
            yield

        else:
            if self.soup == None:
                self.get_html()
            soup = self.soup

            s = soup.find_all('div', class_='zm-item-answer')
            for j in range(len(s)):
                vote_count = s[j].find('span', class_='count').get_text()

                # 非匿名
                if s[j].find('a', class_='author-link') is not None:
                    auth = s[j].find('a', class_='author-link').get_text()
                    # auth_url = s[j].find('a', class_='author-link')['href']
                else:
                    auth = s[j].find('span', class_='name').get_text()
                content = s[j].find('div', class_='zm-editable-content clearfix').get_text()
                yield (auth, vote_count, content)

    def to_txt(self):
        file_name = self.get_title().replace('\n', '')
        items = self.get_all_answers()
        if os.path.exists(os.path.join(os.getcwd(), file_name)):
            with open(os.path.join(os.getcwd(), file_name), 'w') as f:
                f.write('\n')
        else:
            os.mkdir(os.path.join(file_name))
            for auth, vote, content in items:
                with open(os.path.join(os.getcwd(), file_name + '\\' + auth + '的回答' + '----' + \
                        '获赞数：' + str(vote) + '.txt'), 'w') as f:
                    f.write(content)
                    print('Author: {0} Vote: {1} Content: {2}'.format(auth, vote, content))
                    print('-@#-'*10)
        print('--**--已经存为txt!!')


class User:
    # user_url = None
    soup = None

    def __init__(self, user_url, user_name=None):
        if not re.compile(r"^(http|https)://w{3}\.zhihu\.com/people/\S+$").match(user_url):
            raise ValueError('\"' + user_url + '\"' + "it isn't a user url.")
        else:
            self.user_url = user_url
            if user_name != None:
                self.user_name = user_name

    def get_html(self):
        r = session.get(self.user_url)
        self.soup = BeautifulSoup(r.content, 'lxml')

    def get_user_name(self):
        # if self.user_url == None:
            # print('url: ', user)
        #     return '12匿名用户'
        # else:
        if hasattr(self, 'user_name'):
            return self.user_name
        else:
            if self.soup == None:
                self.get_html()
            user_name = self.soup.find('span', class_='name').span
            if user_name != None:
                self.user_name = user_name.string
                return user_name

    def user_description(self):
        if self.soup == None:
            self.get_html()
        s = self.soup.find('span', class_='content')
        if s != None:
            self_description = s.string
            return self_description
        else:
            return None

    def get_agree_num(self):
        if self.user_url == None:
            return 0
        else:
            if self.soup == None:
                self.get_html()
            num = self.soup.find('span', class_='zm-profile-header-user-agree').strong
            print('num: ', num)
            if num != None:
                get_agree_num = num.string
                return get_agree_num
            else:
                return 0
