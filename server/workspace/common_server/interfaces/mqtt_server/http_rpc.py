#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
import ujson
import urllib2
from utils.crypto.beiqi_sign import append_url_sign_tk


def get_status(server_ip, tk, app_secret, user_list, port=8203):
    """
    获取状态
    :param server_ip: 服务器ip
    :param tk:  tk
    :param app_secret:
    :param user_list:  用户列表，list形式
    :param port:
    :return:
    """
    url = 'http://{ip}:{port}/get_status?user_list={user_list}'.format(ip=server_ip, port=port, user_list=ujson.dumps(user_list))
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())