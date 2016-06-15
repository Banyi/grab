#!/user/bin/env python3
# _*_ coding: utf-8 _*_

import re
import os
import requests
from bs4 import BeautifulSoup


#session = requests.Session()



class Question:
    soup = None
    url = None

    def __init__(self, url, title=None):
        if not re.compile(r'(http|https)://w{3}\.zhihu\.com/question/\d{8}').match(url):
            raise ValueError("\"" + url + "\"" + ": it isn't a question url")
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




class User:
    HOME_URL = 'http://www.zhihu.com'
    soup = None

    def __init__(self, user_url):
        if not re.compile(r"^(http|https)://w{3}\.zhihu\.com/people/\S+$").match(user_url):
            raise ValueError('\"' + user_url + '\"' + "it isn't a user url.")
        else:
            self.user_url = user_url

    def get_html(self):
        r = session.get(self.user_url)
        self.soup = BeautifulSoup(r.content, 'lxml')

    def get_user_name(self):
        if self.soup == None:
            self.get_html()
        user_name = self.soup.find('span', class_='name')
        # print('@@User Name: ', user_name)
        if user_name != None:
            user_name = user_name.string
            return user_name

    def user_description(self):
        if self.soup == None:
            self.get_html()
        s = self.soup.find('span', class_='content')
        if s != None:
            self_description = s.get_text()
            return self_description
        else:
            return None

    def get_agree_num(self):
        if self.user_url == None:
            return 0
        else:
            if self.soup == None:
                self.get_html()
            agree_num = self.soup.find('span', class_='zm-profile-header-user-agree').strong

            if agree_num != None:
                get_agree_num = agree_num.string
                return get_agree_num
            else:
                return 0

    def get_thanks(self):
        if self.user_url == None:
            return 0
        else:
            if self.soup == None:
                self.get_html()
            thanks_num = self.soup.find('span', class_='zm-profile-header-user-thanks').strong
            if thanks_num != None:
                get_thanks_num = thanks_num.string
                return get_thanks_num
            else:
                return 0

    def get_asks(self):
        if self.user_url == None:
            return 0
        else:
            if self.soup == None:
                self.get_html()
            ask_item = self.soup.find_all('a', class_='item')[1]
            num = ask_item.span
            if (num and ask_item) != None:
                asks_num = num.string
                ask_item_url = self.HOME_URL + ask_item['href']
                return (asks_num, ask_item_url)

    def get_user_answer(self):
        if self.user_url == None:
            return 0
        else:
            if self.soup == None:
                self.get_html()
            num = self.soup.find_all('a', class_='item')[2]
            if num != None:
                answer_num = num.span.string
                answer_url = self.HOME_URL + num['href']
                return (answer_num, answer_url)

    def get_followees(self):
        if self.user_url == None:
            print('--followee_num--')
            return 0
        else:
            if self.soup == None:
                self.get_html()
            followee = self.soup.find('div', class_='zm-profile-side-following zg-clear')\
                    .find('a', class_='item').strong
            if followee != None:
                followee_num = followee.string
                return followee_num
            else:
                return 0

    def get_followers(self):
        if self.user_url == None:
            print('++followers_num++')
            return 0
        else:
            if self.soup == None:
                self.get_html()
            follower = self.soup.find('div', class_='zm-profile-side-following zg-clear')\
                    .find_all('a', class_='item')[1].strong
            if follower != None:
                follower_num = follower.string
                return follower_num
            else:
                return 0


class Answer:
    soup = None
    url = None
    HOME_URL = 'http://www.zhihu.com'

    def __init__(self, url):
        if not re.compile(r"^(http|https)://w{3}\.zhihu\.com/question/\d{8}$").match(url):
            raise ValueError('\"' + url + '\"' + "it isn't a question url.")

        self.url = url

    def get_html(self):
        r = session.get(self.url)
        self.soup = BeautifulSoup(r.content, 'lxml')

    # def get_question(self):
    #    if hasattr(self, 'question'):
    #        return self.question
    #    else:
    #        if self.soup == None:
    #            self.get_html()
    #       question_url = self.find('h2', class_='zm-item-title zm-editable-content')

    def get_all_content(self):
        if self.soup == None:
            self.get_html()
        soup = self.soup
        # print('soup: ', soup)
        # soup = BeautifulSoup(soup, 'lxml')
        answers = soup.find('div', id='zh-question-answer-wrap')
        soup.body.extract()
        soup.head.insert_after(soup.new_tag('body', {'class': 'zhi'}))
        soup.body.append(answers)
        print('--=0ew-r9w0er')
        return soup

    def to_txt(self):
        content = self.get_all_content()
        body = content.find('body')
        print('-------content------')

        br_list = body.find_all('br')
        for br in br_list:
            br.insert_after(content.new_string('\n'))

        li_list = body.find_all('li')
        for li in li_list:
            li.insert_before(content.new_string('\n'))

        question = Question(self.url)

        file_name = question.get_title().replace('\n', '')

        # items = content.find_all('div', )
        items = content.find_all('div', class_='zm-item-answer')
        if items != None:
            for j in range(len(items)):
                vote_count = items[j].find('span', class_='count').get_text()

                # 非匿名
                if items[j].find('a', class_='author-link') is not None:
                    auth = items[j].find('a', class_='author-link').get_text()
                    auth_url = items[j].find('a', class_='author-link')['href']
                else:
                    auth = items[j].find('span', class_='name').get_text()
                content = items[j].find('div', class_='zm-editable-content clearfix').get_text()
                yield (auth, vote_count, auth_url, content)

            print('=^^&'*10)


        if os.path.exists(os.path.join(os.getcwd(), file_name)):
            with open(os.path.join(os.getcwd(), file_name), 'w') as f:
                f.write('\n')
        else:
            os.mkdir(os.path.join(file_name))
            for auth, vote, auth_url, content in items:
                with open(os.path.join(os.getcwd(), file_name + '\\' + file_name + '---' + auth + \
                        '的回答' + '.txt'), 'w') as f:
                    f.write(str('作者链接: ') + self.HOME_URL + auth_url)
                    f.write(content)
                    # print('Author: {0} Vote: {1} Content: {2}'.format(auth, vote, content))
                    # print('-@#-'*10)
        print('--**--已经存为txt!!')
