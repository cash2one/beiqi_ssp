#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/20

@author: Jay
"""
import urllib2
import urllib
import json
from util.filetoken import gen_file_tk


def up_beiqi_file(user_name, file_type, fn, file_body, up_file_url='http://localhost:8106/up?'):
    """
    上传贝启文件
    :param user_name:  发送者用户名
    :param file_type: 文件类型
    :param fn:  文件名
    :param file_body:  文件内容，二进制
    :param up_file_url: 贝启文件上传地址
    :return: ref: 文件ref
    """
    ul = 1
    by_app = 0
    tk = gen_file_tk(user_name, fn, ul, by_app)
    up_args = {'tk': tk, 'src': file_type, 'by': user_name, 'usage': 'share'}
    resp = urllib2.urlopen(urllib2.Request(up_file_url + urllib.urlencode(up_args), file_body)).read()
    resp = json.loads(resp)
    return resp.get('r')


def down_beiqi_file(user_name, fn, ref, down_file_url='http://localhost:8106/down?tk={tk}&r={ref}'):
    """
    下载贝启文件
    :param user_name: 用户名
    :param fn:  文件名
    :param ref: 文件ref
    :param down_file_url: 贝启文件下载地址
    :return:  file_body
    """
    tk = gen_file_tk(user_name, fn, 0, 0)
    file_url = down_file_url.format(tk=tk, ref=ref)
    return urllib2.urlopen(file_url).read()


