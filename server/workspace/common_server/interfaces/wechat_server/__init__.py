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
WECHAT_CUSTOMER_SERVICE_URL = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'

def wechat_file_up(access_token, file_url, fn, file_type="voice"):
    """
    微信文件上传
    :param access_token: 微信访问码
    :param file_url:  文件url
    :param fn:  文件名
    :return:
    """
    file_flag = fn.split('.')[-1]
    filetype='%s/%s' % (file_type, file_flag)
    param = MultipartParam(name='media', filename=fn, filetype=filetype, fileobj=StringIO.StringIO(urllib2.urlopen(file_url).read()))
    datagen, headers = multipart_encode({"media": param})

    # 创建请求对象
    request = urllib2.Request(WECHAT_FILE_UP_URL.format(access_token=access_token, type=file_type), datagen, headers)
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


def wechat_customer_service(access_token, payload):
    """
    微信客服反馈
    :param access_token: 访问码
    :param payload:  反馈内容
    :return:
    """
    customer_url = WECHAT_CUSTOMER_SERVICE_URL.format(access_token=access_token)
    return urllib.urlopen(customer_url, ujson.dumps(payload, ensure_ascii=False)).read()