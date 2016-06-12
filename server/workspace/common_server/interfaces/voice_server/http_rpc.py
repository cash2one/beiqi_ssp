#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/12

@author: Jay
"""


def audio_ai(http_rpc_client, file_data):
    """
    语音ai
    :param http_rpc_client: http连接
    :param file_data:  文件内容
    """
    url = "audio_ai"
    headers = { 'Content-Type': 'application/octet-stream'}
    return http_rpc_client.fetch_async(url, headers, body=file_data)
