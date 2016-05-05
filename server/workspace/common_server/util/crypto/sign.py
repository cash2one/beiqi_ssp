#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
import urllib
from hashlib import md5

def sign(http_method, url, params, secret_key):
    """
    签名
    :param http_method:  http访问方法
    :param url:  http访问url
    :param params:  去除_tk和_sign之后的所有参数
    :param secret_key: secret_key
    :return:
    """
    params_keys = params.keys()
    params_keys.sort()
    params_str = "".join(["%s=%s" % (urllib.unquote(str(key)), urllib.unquote(str(params[key]))) for key in params_keys])
    base_str = http_method + url + params_str + secret_key
    base_urlenc_str = urllib.quote(base_str, safe='')
    md5_inst = md5()
    md5_inst.update(base_urlenc_str)
    return md5_inst.hexdigest()