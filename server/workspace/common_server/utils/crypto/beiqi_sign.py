#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
import time
import urllib
from hashlib import md5
from utils import logger
from util.sso_common.build_sso_token import parser_token

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


def beiqi_tk_sign_wapper():
    def parse_request(self, *args, **kwargs):
        method = self.request.method
        url = "http://" + self.request.host + self.request.uri
        sign = kwargs.pop('_sign', None)
        token = kwargs.pop('_tk', None)
        return method, url, sign, token, kwargs

    def beiqi_tk_sign_fun_wapper(fun):
        def beiqi_tk_sign_param_wapper(self, *args, **kwargs):
            method, url, expect_sign, auth_token, params = parse_request(self, *args, **kwargs)
            if not expect_sign or not auth_token:
                logger.error("%s not expect_sign:%s or not auth_token:%s"%(fun.__name__, expect_sign, auth_token))
                self.set_status(401)
                return

            expire, secret_key, account, apikey_head4 = parser_token(auth_token)
            if expire <= time.time():
                logger.error("%s expire:%s invalid"%(fun.__name__, expire))
                self.set_status(401)
                return

            cal_sign = sign(method, url, params, secret_key)
            if cal_sign != expect_sign:
                logger.error("%s cal_sign:%s != expect_sign:%s"%(fun.__name__, cal_sign, expect_sign))
                self.set_status(401)
                return

            kwargs['user_name'] = account
            return fun(self, *args, **kwargs)
        return beiqi_tk_sign_param_wapper
    return beiqi_tk_sign_fun_wapper
