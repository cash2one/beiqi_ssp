#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
import ujson
import urllib2
from utils.crypto.beiqi_sign import append_server_sign


def get_status(server_ip, user_list, port=8203):
    """
    获取状态
    :param server_ip: 服务器ip
    :param user_list:  用户列表，list形式
    :param port:
    :return:
    """
    url = 'http://{ip}:{port}/get_status?user_list={user_list}'.format(ip=server_ip, port=port, user_list=ujson.dumps(user_list))
    url = append_server_sign(url)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def beiqi_msg_bcast(server_ip, gid, payload, port=8203):
    """
    贝启消息广播
    :param server_ip: 服务器ip
    :param gid:  gid
    :param payload: mqtt:pyalod
    :param port:
    :return:
    """
    url = 'http://{ip}:{port}/beiqi_msg_bacst?gid={gid}&payload={payload}'.format(ip=server_ip, port=port, gid=gid, payload=payload)
    url = append_server_sign(url)
    return urllib2.urlopen(urllib2.Request(url)).read()


def beiqi_msg_p2p(server_ip, sn, payload, port=8203):
    """
    贝启消息广播
    :param server_ip: 服务器ip
    :param sn:  设备sn
    :param payload: mqtt:pyalod
    :param port:
    :return:
    """
    url = 'http://{ip}:{port}/beiqi_msg_p2p?sn={sn}&payload={payload}'.format(ip=server_ip, port=port, sn=sn, payload=payload)
    url = append_server_sign(url)
    return urllib2.urlopen(urllib2.Request(url)).read()