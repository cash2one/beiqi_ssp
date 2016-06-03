#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/19

@author: Jay
"""
import os
import json
import urllib2
import time
from ctypes import *
from util.catch import except_adaptor
from voice_server.setting import *


libkdxf_voice = cdll.LoadLibrary('libkdxf_voice.so')
libkdxf_voice.voice_2_text.restype = c_char_p
libkdxf_voice.voice_2_text.argtypes=[c_char_p, c_long, c_int]
libkdxf_voice.text_2_voice.restype = c_int
libkdxf_voice.text_2_voice.argtypes=[c_char_p, c_char_p]
libkdxf_voice.msp_login.restype = c_int
ret = libkdxf_voice.msp_login(KDXF_MSC_APP_ID)
assert ret == 0


@except_adaptor(is_raise=False)
def tuling_ai(text, loc="北京市中关村"):
    """
    图灵AI智能回答
    :param user_id: 用户id
    :param text: 文本
    :param loc: 位置
    :return: 文本/None
    """
    params = {
        "key": TULING_API_KEY,
        "info": text,
        "loc": loc,
        "userid": "user_id"
    }

    json_data = json.dumps(params)
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Content-length": len(json_data)}

    ai_result = json.loads(urllib2.urlopen(urllib2.Request(TULING_AI_URL,json_data, headers)).read())
    text = ai_result['text']
    return text.encode('utf8') if isinstance(text, unicode) else text

@except_adaptor(is_raise=False)
def kdxf_msc_voice2text(file_data):
    """
    科大讯飞 msc 语音转成文本
    :param file_data: 语音格式数据
    :return: 识别到的文本/None
    """
    text = libkdxf_voice.voice_2_text(c_char_p(file_data), c_long(len(file_data)), c_int(0))
    return text.encode('utf8') if isinstance(text, unicode) else text


@except_adaptor(is_raise=False)
def kdxf_msc_text2voice(text):
    """
    科大讯飞 文本转语音
    :param text: 文本
    :return: 语音格式， 语音数据/None
    """
    tmp_file = "%s.wav"%(int(time.time()))
    libkdxf_voice.text_2_voice(c_char_p(text), c_char_p(tmp_file))

    file_data = open(tmp_file).read()
    os.remove(tmp_file)
    return tmp_file, file_data


# def get_baidu_vop_token():
#     token = account_cache.send_cmd(*get_beiqi_vop_token())
#     if not token:
#         gen_token_result = json.loads(urllib2.urlopen(urllib2.Request(BAIDU_VOP_TOKEN_URL)).read())
#         token = gen_token_result['access_token']
#         expires = gen_token_result['expires_in']
#         account_cache.send_cmd(*set_beiqi_vop_token(token,expires))
#     return token
#
#
# @except_adaptor(is_raise=False)
# def baidu_vop_voice2text(user_id, fn, file_data):
#     """
#     百度vop 语音转成文本
#     :param user_id: 用户id
#     :param fn : 文件名， xxx.mp3/wav/.....
#     :param file_data: 语音格式数据
#     :return: 识别到的文本/None
#     """
#     data = {
#         "format": fn.split('.')[-1],
#         "rate": 8000,
#         "channel": 1,
#         "token": get_baidu_vop_token(),
#         "cuid": user_id,
#         "len": len(file_data),
#         "speech": base64.b64encode(file_data),
#     }
#
#     json_data = json.dumps(data)
#     headers = {"Content-Type": "application/json; charset=utf-8",
#                "Content-length": len(json_data)}
#
#     vop_result = json.loads(urllib2.urlopen(urllib2.Request(BAIDU_VOP_VIOCE2TEXT_URL, json_data,headers)).read())
#     logger.debug('baidu_vop_voice2text vop_result: %s' % vop_result)
#     text = vop_result['result'][0]
#     return text.encode('utf8') if isinstance(text, unicode) else text
#
#
# @except_adaptor(is_raise=False)
# def baidu_vop_text2voice(user_id, text):
#     """
#     百度vop 文本转语音
#     :param user_id: 用户id
#     :param text: 文本
#     :return: 语音格式， 语音数据/None
#     """
#     text = text.encode('utf-8') if isinstance(text, unicode) else text
#     text2audio_url = BAIDU_VOP_TEXT2AUDIO_URL.format(
#         text=urllib2.quote(text),
#         access_token=urllib2.quote(get_baidu_vop_token()),
#         cuid=urllib2.quote(user_id))
#
#     voice_data = urllib2.urlopen(urllib2.Request(text2audio_url)).read()
#     return "mp3", voice_data




