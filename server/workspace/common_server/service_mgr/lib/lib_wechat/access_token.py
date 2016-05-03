#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-14

@author: Jay
"""
from utils.setting.wechat import CLIENT_ACCESS_TOKEN_URL, UAUTH_ACCESSS_TOKEN_URL
from utils.network.http import HttpRpcClient
from utils.meta.singleton import Singleton
from utils import logger
from utils.scheduler import Jobs
from utils.wapper.stackless import gevent_adaptor
from utils.wechat.ierror import WXBizMsgCrypt_OK
import traceback

CLT_ACCESSTOKEN_REFRESH_TIME = (60 * 60)


class CltAccessTokenGetter(object):
    """
    access_token是公众号的全局唯一票据，公众号调用各接口时都需使用access_token。开发者需要进行妥善保存。
    access_token的存储至少要保留512个字符空间。access_token的有效期目前为2个小时，需定时刷新，
    重复获取将导致上次获取的access_token失效。
    http://mp.weixin.qq.com/wiki/11/0e4b294685f817b95cbed85ba5e82b8f.html
    """
    __metaclass__ = Singleton

    def __init__(self):
        self._access_token = None
        self._get()
        Jobs().add_interval_job(CLT_ACCESSTOKEN_REFRESH_TIME, self._get)

    @gevent_adaptor(use_join_result=False)
    def _get(self):
        try:
            result = eval(HttpRpcClient(ssl=True).fetch_async(CLIENT_ACCESS_TOKEN_URL))
            assert isinstance(result, dict)
            assert "errcode" not in result, result
        except:
            logger.error(traceback.format_exc())
            return None

        self.access_token = result['access_token']

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, new_access_token):
        self._access_token = new_access_token
        logger.info("CltAccessTokenGetter::access_token new wechat access_token:%s" % self._access_token)


class UserAuthInfoGetter(object):
    """
    微信用户授权AccessToken机制
    微信公众平台OAuth2.0授权

    如果用户在微信客户端中访问第三方网页，公众号可以通过微信网页授权机制，来获取用户基本信息，进而实现业务逻辑。
    http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.auth_info_dic = {}

    @gevent_adaptor(use_join_result=True)
    def _gen_auth_info(self, code):
        try:
            result = eval(HttpRpcClient(ssl=True).fetch_async(UAUTH_ACCESSS_TOKEN_URL(code)))
            assert isinstance(result, dict)
            assert "errcode" not in result or result['errcode'] == WXBizMsgCrypt_OK, result
            assert "access_token" in result, result
            assert "refresh_token" in result, result
            assert "openid" in result, result
        except:
            logger.error(traceback.format_exc())
            return None

        self.auth_info_dic[code] = result
        return result

    def get_openid(self, code):
        auth_info = self.auth_info_dic.get(code, self._gen_auth_info(code))
        return auth_info.get('openid',None) if auth_info else None



