#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import ujson
import urllib2
from utils.crypto.beiqi_sign import append_url_sign_tk, gen_url_sign


def sign_in(server_ip, tk, app_secret, sn, port=8302):
    url = 'http://{ip}:{port}/sign_in?sn={sn}'.format(ip=server_ip, port=port, sn=sn)
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())


def loc_v1(server_ip, tk, app_secret, sn, payload,  port=8302):
    url = 'http://{ip}:{port}/loc_v1'.format(ip=server_ip, port=port)
    _sign = gen_url_sign(url, app_secret, 'POST')
    data = 'sn={sn}&payload={payload}&_tk={tk}&_sign={sign}'.format(sn=sn, payload=payload, tk=tk, sign= _sign)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url, data=data)).read())