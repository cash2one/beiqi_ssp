#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""
import urllib
import urllib2
import StringIO
import ujson
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers

# 在 urllib2 上注册 http 流处理句柄
register_openers()


WECHAT_FILE_UP_URL = "http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={type}"
WECHAT_FILE_DOWN_URL = "http://file.api.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}"

def wechat_file_up(access_token, file_url, fn):
    """
    微信文件上传
    :param access_token: 微信访问码
    :param file_url:  文件url
    :param fn:  文件名
    :return:
    """
    file_type_flag = fn.split('.')[-1]
    filetype='voice/%s' % (file_type_flag)
    param = MultipartParam(name='media', filename=fn, filetype=filetype, fileobj=StringIO.StringIO(urllib2.urlopen(file_url).read()))
    datagen, headers = multipart_encode({"media": param})

    # 创建请求对象
    type='voice'
    request = urllib2.Request(WECHAT_FILE_UP_URL.format(access_token=access_token, type=type), datagen, headers)
    return ujson.loads(urllib2.urlopen(request).read())

def wechat_file_down(access_token, media_id):
    """
    微信文件下载
    :param access_token: 微信访问码
    :param media_id:  微信文件id
    :return:
    """
    wechat_down_url = WECHAT_FILE_DOWN_URL.format(access_token=access_token, media_id=media_id)
    return urllib.urlopen(wechat_down_url).read()