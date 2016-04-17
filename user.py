#!/user/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import random
import requests
import platform
import termcolor
import http.cookiejar


requests = requests.session()
requests.cookies = http.cookiejar.LWPCookieJar(filename='cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    pass


class Logging:
    flag = True

    @staticmethod
    def error(msg):
        if Logging.flag == True:
            print("".join([termcolor.colored("ERROR", "red"), ":", termcolor.colored(msg, "white")]))

    @staticmethod
    def warm(msg):
        if Logging.flag == True:
            print("".join([termcolor.colored("WARN", "yellow"), ": ", termcolor.colored(msg, 'white')]))

    @staticmethod
    def info(msg):
        if Logging.flag == True:
            print("".join([termcolor.colored("INFO", "magenta"), ":", termcolor.colored(msg, "white")]))

    @staticmethod
    def debug(msg):
        if Logging.flag == True:
            print("".join([termcolor.colored("DEBUG", "magenta"), ":", termcolor.colored(msg, "white")]))

    @staticmethod
    def success(msg):
        if Logging.flag == True:
            print("".join([termcolor.colored("SUCCSE", "green"), ":", termcolor.colored(msg, "white")]))

Logging.flag = True

class LoginPasswordError(Exception):
    def __init__(self, msg):
        if isinstance(msg, str):
            self.msg = msg
        else:
            self.msg = u"账号密码错误"
            Logging.error(self.msg)

class NetworkError(Exception):
    def __init__(self, msg):
        if isinstance(msg, str):
            self.msg = msg
        else:
            self.msg = u'网络异常'
            Logging.error(self.msg)

class AcconutError(Exception):
    def __init__(self, msg):
        if isinstance(msg, str):
            self.msg = msg
        else:
            self.msg = u'账号异常'
            Logging.error(self.msg)


def download_captcha():
    url = "http://www.zhihu.com/captcha.gif"
    r = requests.get(url, params={"r": random.random(), 'type': 'login'})
    if int(r.status_code) != 200:
        raise NetworkError(u'验证码请求失败')
    image_name = u'verify.' + r.headers['content-type'].split("/")[1]
    open(image_name, "wb").write(r.content)
    """
       System platform: https://docs.python.org/2/liberary/platform.html
    """
    Logging.info(u"正在调用外部程序渲染验证码...")
 
    if platform.system() == "Windows":
        os.system("%s &" % image_name)
    else:
        Logging.info(u"无法探测你的作业系统，请自行打开验证码 % 文件，并输入验证码。" % os.path.join(os.getcwd(), image_name))

    sys.stdout.write(termcolor.colored(u"请输入验证码：", "cyan"))
    captcha_code = input()
    return captcha_code

def search_xsrf():
    url = "http://www.zhihu.com/"
    r = requests.get(url)
    if int(r.status_code) != 200:
        raise NetworkError(u"验证码请求失败！")
    results = re.compile(r"\<input\stype=\"hidden\"\sname=\"_xsrf\"\svalue=\"(\S+)\"", re.DOTALL).findall(r.text)
    if len(results) < 1:
        Logging.info(u'提取XSRF代码失败！')
        return None
    return results[0]

def build_form(account, password):
    if re.match(r"^1\d{10}$", account):
        account_type = "phone_num"
    elif re.match(r"^\S+\@\S+\.\S+$", account):
        account_type = "email"
    else:
        raise AcconutError(u"账号类型错误")

    form = {account_type: account, "password": password, 'remenber_me': True}

    form['_xsrf'] = search_xsrf()
    form['captcha'] = download_captcha()
    return form

def upload_form(form):
    if "email" in form:
        url = "http://www.zhihu.com/login/email"
    elif "phone_num" in form:
        url = "http://www.zhihu.com/login/phone_num"
    else:
        raise ValueError(u"账号类型错误")

    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        'Host': "www.zhihu.com",
        'Origin': "http://www.zhihu.com",
        'Pragma': "no-cache",
        'Referer': "http://www.zhihu.com/",
        'X-Requested-With': "XMLHttpRequest"
    }

    r = requests.post(url, data=form, headers=headers)
    if int(r.status_code) != 200:
        raise NetworkError(u"表单上传失败！")

    if r.headers['content-type'].lower() == "application/json":
        try:
            result = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            Logging.error(u'JSON解析失败！')
            Logging.debug(e)
            Logging.debug(r.content)
            result = {}

        print(result)

        if result["r"] == 0:
            Logging.success(u"登录成功!")
            return {"result": True}
        elif result["r"] == 1:
            Logging.info(u"登录失败！")
            return {"error": {"code": int(result['errcode']), "message": result['msg'], "data": result['data']}}
        else:
            Logging.warm(u"表单上传出现未知错误: \n \t %s)" % (str(result)))
            return {"error": {"code": -1, "message": u"unknown error"}}
    else:
        Logging.warm(u"无法解析服务器的响应内容：\n \t %s " % r.text)
        return {"error": {"code": -2, "message": u"parse error"}}

def islogin():
    url = "http://www.zhihu.com/settings/profile"
    r = requests.get(url, allow_redirects=False)
    status_code = int(r.status_code)
    if status_code == 301 or status_code == 302:
        return False
    elif status_code == 200:
        return True
    else:
        Logging.warm(u"网络故障")
        return None

def read_account_from_config_file(config_file="config.ini"):
    try:
        import configparser
    except:
        from six.moves import configparser
    cf = configparser.ConfigParser()
    if os.path.exists(config_file) and os.path.isfile(config_file):
        Logging.info(u"正在加载配置文件...")
        cf.read(config_file)

        email = cf.get("info", "email")
        password = cf.get("info", "password")
        if email == "" or password == "":
            Logging.warm(u"账户信息无效")
            return (None, None)
        else:
            return (email, password)
    else:
        return (None, None)

def login(account=None, password=None):
    if islogin() == True:
        Logging.success(u"你已经登录成功!")
        return True

    if account == None:
        (account, password) = read_account_from_config_file()
    if account == None:
        sys.stdout.write(u"请输入登录账户: ")
        account = input()
        sys.stdout.write(u"请输入登录密码: ")
        password = input()

    form_data = build_form(account, password)

    result = upload_form(form_data)
    if 'error' in result:
        if result['error']['code'] == 1991829:
            Logging.error(u'验证码输入错误，请重新输入')
            return login()
        elif result['error']['code'] == 100005:
            Logging.error(u'密码输入错误！请重新输入')
            return login()
        else:
            Logging.warm(u'未知错误！')
            return False
    elif 'result' in result and result['result'] == True:
        Logging.success(u"登录成功!")
        requests.cookies.save()
        return True


if __name__ == "__main__":
    login()
