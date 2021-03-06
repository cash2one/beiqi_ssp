#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-21

@author: Jay
"""
import ujson
import urllib2


def req_reg_val_code(http_rpc_client, account):
    """
    发送注册短信验证码
    :param http_rpc_client:
    :param account:
    :return:
    """
    url = "req_reg_val_code?account=%s"%account
    return ujson.loads(http_rpc_client.fetch_async(url))


def gen_tk(http_rpc_client, user_name, pwd, app_key, rc4_key=""):
    url = "gen_tk?username={0}&pwd={1}&api_key={2}&rc4_key={3}".format(urllib2.quote(user_name), urllib2.quote(pwd), urllib2.quote(app_key), urllib2.quote(rc4_key))
    return http_rpc_client.fetch_async(url)


def check_reg_val_code(http_rpc_client, account, pwd, val):
    """
    验证注册短信验证码
    :param http_rpc_client:
    :param account:
    :param pwd:
    :param val:
    :return:
    """
    url = "check_reg_val_code?account=%s&pwd=%s&val=%s"%(account, pwd, val)
    return ujson.loads(http_rpc_client.fetch_async(url))
