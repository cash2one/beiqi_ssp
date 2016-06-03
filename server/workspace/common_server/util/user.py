#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/12

@author: Jay
"""
from util.redis_cmds.circles import get_gid_of_sn, get_user_groups, get_wechat_gids

def is_device_user(acc):
    return "@" not in acc and "wx#" not in acc

def is_wechat_user(acc):
    return "@" not in acc and "wx#" in acc

def is_app_user(acc):
    """
    是否是app用户，包括ios，android用户
    :param acc: 
    :return: 
    """
    return "@" in acc


def get_user_gids(acc, dev_filter=dev_filter):
    """
    获取关联的gid列表
    :param acc: 用户
    :param dev_filter: redis 连接
    :return:
    """
    if is_device_user(acc):
        gid_list = [dev_filter.send_cmd(*get_gid_of_sn(acc))]
    elif is_wechat_user(acc):
        gid_list = dev_filter.send_cmd(*get_wechat_gids(acc))
    else:
        gid_list = dev_filter.send_cmd(*get_user_groups(acc))
    return gid_list
