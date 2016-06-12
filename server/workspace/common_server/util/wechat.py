#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import ujson
import time
from utils import logger
from utils.network.http import HttpRpcClient
from util.redis_cmds.wechat import get_wechat_access_token, set_wechat_access_token, get_wechat_ticket, set_wechat_ticket


APPID = 'wxd0334fe5bbc270d2'
APPSECRET = '6d2f605d568f6a66f2acd6736befa8e3'
WX_GET_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(APPID, APPSECRET)
WX_GET_TICKER_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token={access_token}'


def gen_wechat_access_token(redis_ints):
    """
    自动获取wechat授权访问码，如果不存在则创建之
    :param redis_ints: redis 对象
    :return: access_token
    """
    access_token = redis_ints.send_cmd(*get_wechat_access_token())
    if access_token:
        return access_token

    get_token_result = ujson.loads(HttpRpcClient().fetch_async(url=WX_GET_ACCESS_TOKEN_URL))
    access_token = get_token_result.get('access_token')
    assert access_token, 'get wechat access token failed. errcode: %r, errmsg: %r' % (get_token_result.get('errcode'), get_token_result.get('errmsg'))
    expires = get_token_result.get('expires_in')

    redis_ints.send_cmd(*set_wechat_access_token(access_token, expires))
    logger.debug('get_access_token:%s, access_token=%s, expires_in=%s', time.strftime('%Y-%d-%m %H:%M:%S', time.localtime()), access_token, expires)
    return access_token


def gen_wechat_ticker(redis_ints, access_token):
    """
    自动获取wehcat ticker，如果不存在则创建之
    :param redis_ints:  redis 对象
    :param access_token: 微信授权访问码
    :return: ticker
    """
    ticker = redis_ints.send_cmd(*get_wechat_ticket())
    if ticker:
        return ticker

    get_ticket_result = ujson.loads(HttpRpcClient().fetch_async(url=WX_GET_TICKER_URL.format(access_token=access_token)))
    ticker = get_ticket_result.get("ticker")
    ticker_exp = get_ticket_result.get('expires_in')

    redis_ints.send_cmd(*set_wechat_ticket(ticker, ticker_exp))
    logger.debug('get_ticker:%s, ticker=%s, expires_in=%s', time.strftime('%Y-%d-%m %H:%M:%S', time.localtime()), ticker, ticker_exp)
    return ticker