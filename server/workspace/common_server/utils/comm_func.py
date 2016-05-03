# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import platform
import os
import inspect
import time
import datetime
import random
import uuid


def get_log_path(server_name=None):
    sys_platform = platform.system()
    if sys_platform == 'Linux':
        log_path = "/var/log/td/"
    else:
        log_path = "C:\\td\\"
    if server_name:
        log_path = os.path.join(log_path, server_name)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return log_path


def is_code_module(module):
    """
    检查模块是否是代码模块
    @param module:
    """
    try:
        return inspect.getsourcefile(module) or ''
    except TypeError:
        return ''


def set_attr(attr_name, orm=None, client=None):
    def _swap(func):
        def __swap(*args, **kwargs):
            res = func(*args, **kwargs)
            self = args[0]
            if orm:
                orm_obj = self.__dict__.get(orm)
                orm_obj.update(attr_name)
            if client:
                client_obj = self.__dict__.get(client)
                client_obj.set_dirty_flag(attr_name)
            return res
        return __swap
    return _swap


def import_handlers(seach_path, import_path, excluded_files=None):
    """
    auto import python modules in a directory
    :param seach_path:  the path to seach the .py files
    :param import_path: the path to import the .py files , sub path of the seach_path
    :param excluded_files: excluded files
    :return:
    """
    if excluded_files is None:
        excluded_files = []
    for _, _, filenames in os.walk(seach_path):
        for filename in filenames:
            if filename.endswith(".py") and filename not in excluded_files:
                exec "from %s import %s" % (import_path, filename.split('.')[0])


def sub_dict(somedict, somekeys, default=None):
    return dict([ (k, somedict.get(k, default)) for k in somekeys ])

def datetime_to_string(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def string_to_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

def string_to_timestamp(str_time):
    return time.mktime(string_to_datetime(str_time).timetuple())

def timestamp_to_string(stamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stamp))

def timestamp_to_format_string(stamp, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(stamp))

def datetime_to_timestamp(date_time):
    return time.mktime(date_time.timetuple())

sample_str = "zyxwvutsrqponmlkjihgfedcba123456789"
def random_str(str_len=6):
    assert str_len <= len(sample_str)
    return ''.join(random.sample(sample_str, str_len))


def get_mxadap_host_flag(s_ip, http_port, tcp_port):
    return "%s_%s_%s" % (s_ip, http_port, tcp_port)


def strip_dic_list(dic_list):
    """
    strip 由dict构成的list/tuple
    :param dic_list: [dict,,,,,] / (dict,,,,,)
    :return: None
    """
    if isinstance(dic_list, tuple):
        dic_list = list(dic_list)
    assert isinstance(dic_list, list)

    for dic in dic_list:
        assert isinstance(dic, dict)

        keys = dic.keys()
        for k in keys:
            v = dic.pop(k)
            dic[k.strip()] = v.strip() if isinstance(v, str) or isinstance(v, unicode) else v
            # 以下两种方式，效率慢2倍以上
            # dic.update({key.strip(): dic.pop(key).strip()})
            # dic.__setitem__(key.strip(), dic.pop(key).strip())


def make_unique_id():
    return uuid.uuid1().get_hex()

