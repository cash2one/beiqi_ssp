#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-29

@author: Jay
"""
import os
import random
import string
import io
import time
from code_image_gen import VerifyCode
from utils import logger
from utils.web import cookie, VERIFY_CODE_EXPIRE


def render_verify_code(request_hdl, verify_code_dir=None, cookie_name="verify_code"):
    """
    验证码渲染
    :param request_hdl:http request handler
    :param verify_code_dir: 验证码目录,为空取系统目录
    :param cookie_name:  cookie名称
    :return:None
    """
    random_string = ''.join(random.sample(string.letters+"0123456789", 4))
    code = VerifyCode(random_string, dot=500, line=random.randint(1, 3), line_length=100)
    # 生成的验证码图片 500个麻点 1~3条随机干扰线，干扰线的长度为 100步长
    cookie.set_cookie(request_hdl, cookie_name, code.get_string(), time.time()+VERIFY_CODE_EXPIRE)
    logger.info("render_verify_code, new verify code:%s, ip:%s" % (code.get_string(), request_hdl.request.remote_ip))
    o = io.BytesIO()
    code.get_clip().save(o, format="JPEG")
    s = o.getvalue()
    request_hdl.set_header('Content-type', 'image/jpg')
    request_hdl.set_header('Content-length', len(s))
    request_hdl.write(s)
