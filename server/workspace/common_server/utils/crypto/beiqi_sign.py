#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/5

@author: Jay
"""
import time
import urllib
import urlparse
from hashlib import md5
from utils import logger
from utils.crypto.sign import Signer
from util.sso_common.build_sso_token import parser_token


def sign(http_method, url, params, api_secret):
    """
    签名
    :param http_method:  http访问方法
    :param url:  http访问url
    :param params:  去除_tk和_sign之后的所有参数
    :param api_secret: api_secret
    :return:
    """
    params_keys = params.keys()
    params_keys.sort()
    params_str = "".join(["%s=%s" % (urllib.unquote(str(key)), urllib.unquote(str(params[key]))) for key in params_keys])
    base_str = http_method + url + params_str + api_secret
    base_urlenc_str = urllib.quote_plus(base_str, safe=' ')
    print "base_urlenc_str,",base_urlenc_str
    md5_inst = md5()
    md5_inst.update(base_urlenc_str)
    return md5_inst.hexdigest()


def client_sign_wapper():
    def parse_request(self, *args, **kwargs):
        method = self.request.method
        url = "http://" + self.request.host + self.request.uri
        sign = kwargs.pop('_sign', None)
        token = kwargs.pop('_tk', None)
        return method, url, sign, token, kwargs

    def client_sign_fun_wapper(fun):
        def client_sign_param_wapper(self, *args, **kwargs):
            method, url, expect_sign, auth_token, params = parse_request(self, *args, **kwargs)
            if not expect_sign or not auth_token:
                logger.error("%s not expect_sign:%s or not auth_token:%s"%(fun.__name__, expect_sign, auth_token))
                self.set_status(401)
                return

            expire, api_key, account, apikey_head4 = parser_token(auth_token)
            if expire <= time.time():
                logger.error("%s expire:%s invalid"%(fun.__name__, expire))
                self.set_status(401)
                return

            cal_sign = gen_url_sign(url, api_key, method)
            if cal_sign != expect_sign:
                logger.error("%s cal_sign:%s != expect_sign:%s"%(fun.__name__, cal_sign, expect_sign))
                self.set_status(401)
                return

            # 注意这里需要使用处理过的参数params，不要使用原始参数kwargs
            params['user_name'] = account
            return fun(self, *args, **params)
        return client_sign_param_wapper
    return client_sign_fun_wapper


def server_sign_wapper():
    def server_sign_fun_wapper(fun):
        def server_sign_param_wapper(self, *args, **kwargs):
            sign = kwargs.pop('_sign', None)
            csign = Signer().gen_sign(*kwargs.values())
            if sign != csign:
                logger.error("server_sign_wapper error:values:%r sign:%s csign:%s"%(kwargs.values(), sign, csign))
                self.set_status(401)
                return
            return fun(self, *args, **kwargs)
        return server_sign_param_wapper
    return server_sign_fun_wapper



def gen_url_sign(url, api_secret, method='GET'):
    """
    根据url和api_key获取对应的签名
    :param url:  访问的url
    :param api_secret: api_secret
    :param method: 访问方法
    :return:  签名
    """
    up = urlparse.urlparse(url)
    url = "http://{host}{path}".format(host=up.netloc, path=up.path)
    params = dict([(item.split("=")[0],item.split("=")[1]) for item in up.query.split("&")]) if up.query else {}
    # sigin, tk 不参与服务器再次计算
    params.pop('_sign', None)
    params.pop('_tk', None)
    return sign(method, url, params, api_secret)

def append_url_sign(url, api_secret, method='GET'):
    """
    往url后面添加sign
    :param url:  访问的url
    :param api_secret: api_secret
    :param method: 访问方法
    :return:  签名
    """
    _sign = gen_url_sign(url, api_secret, method)
    splitor = "&" if "?" in url else "?"
    return url + "{splitor}_sign={sign}".format(splitor=splitor, sign=_sign)

def append_url_tk(url, tk):
    """
    往url后面添加tk
    :param url:  访问的url
    :param tk: token
    """
    splitor = "&" if "?" in url else "?"
    return url + "{splitor}_tk={tk}".format(splitor=splitor, tk=tk)

def append_url_sign_tk(url, tk, api_secret, method='GET'):
    """
    往url后面添加tk
    :param url:  访问的url
    :param tk: token
    :param api_key:api_secret
    """
    url = append_url_sign(url, api_secret, method)
    return append_url_tk(url, tk)


def append_server_sign(url):
    """
    服务器间的签名
    :param url:  访问的url
    """
    up = urlparse.urlparse(url)
    params = dict([(item.split("=")[0],item.split("=")[1]) for item in up.query.split("&")]) if up.query else {}
    _sign = Signer().gen_sign(*params.values())
    splitor = "&" if "?" in url else "?"
    return url + "{splitor}_sign={sign}".format(splitor=splitor, sign=_sign)
