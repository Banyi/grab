#!/user/bin/ven python3
# _*_ coding: utf-8 _*_

from grab import Question

url = "https://www.zhihu.com/question/xxxx"

A = Question(url)
'''
title = A.get_title()
print('title: ', title)
item_tag = A.get_item_tag()
print('item_tag: ', item_tag)
detail = A.get_detail()
print('detail: ', detail)
comment = A.get_comment()
print('comment numbers: ', comment)
follower = A.get_follower()
print('follower numbers: ', follower)
'''
# A.get_answers()
answer = A.get_top_i_answer(1)
for i in answer:
    print('answer: ', i)
# print('author: ', author)
