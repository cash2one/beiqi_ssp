#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import ujson
import urllib2
from utils.crypto.beiqi_sign import append_url_sign_tk


def sign_in(server_ip, tk, app_secret, sn, port=8302):
    url = 'http://{ip}:{port}/sign_in?sn={sn}'.format(ip=server_ip, port=port, sn=sn)
    url = append_url_sign_tk(url, tk, app_secret)
    return ujson.loads(urllib2.urlopen(urllib2.Request(url)).read())