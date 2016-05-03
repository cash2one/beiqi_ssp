#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-20

@author: Jay
"""
from utils.service_control.finder import get_cur_ip
import datetime
from utils.comm_func import datetime_to_string
from pandora.setting import VERSION

def get_pandora_info():
    """
    获取当前pandora信息
    :return:
    """
    return {'hostname': get_cur_ip(),
            'datetime': datetime_to_string(datetime.datetime.now()),
            'version': VERSION}
