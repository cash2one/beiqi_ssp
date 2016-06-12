#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/8

@author: Jay
"""
import ujson
import urllib
from util.filetoken import gen_file_tk
from lib_common.file_ul import ul_args_ok
from util.filetoken import gen_lvl_fn
from util.convert import bs2utf8


def up_file(http_rpc_client, user_name, file_type, fn, file_body):
    """
    上传贝启文件
    :param http_rpc_client: http连接
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

    url = "up?%s" % urllib.urlencode(up_args)

    headers = { 'Content-Type': 'application/octet-stream'}
    return ujson.loads(http_rpc_client.fetch_async(url, headers=headers, body=file_body))


def down_file(http_rpc_client, user_name, fn, ref):
    """
    下载贝启文件
    :param http_rpc_client: http连接
    :param user_name: 用户名
    :param fn:  文件名
    :param ref: 文件ref
    :return:  file_body
    """
    tk = gen_file_tk(user_name, fn, 0, 0)
    url = 'down?tk={tk}&r={ref}'.format(tk=urllib.quote(tk), ref=urllib.quote(ref))
    return http_rpc_client.fetch_async(url)


def delete_file(http_rpc_client, user_name, file):
    """
    删除贝启文件
    :param http_rpc_client: http连接
    :param user_name: 用户名
    :param file:  文件名
    :return:  file_body
    """
    url = 'delete_file?file={file}'.format(file=urllib.quote(file))
    return ujson.loads(http_rpc_client.fetch_async(url))


def gen_leveldb_file(CalcRdsInts, user_name, file_type, fn):
    """
    获取leveldb的文件名
    :param CalcRdsInts: rds对象
    :param user_name: 用户名
    :param file_type: 文件类型
    :param fn: 文件名
    :return: file
    """
    ul = 1
    by_app = 0
    usage = 'share'
    tk = gen_file_tk(user_name, fn, ul, by_app)

    tk_params, file_source, usage, unique_sn = ul_args_ok(CalcRdsInts, *(bs2utf8(tk), file_type, usage))
    leveldb_fn = gen_lvl_fn(*tk_params)
    return leveldb_fn
