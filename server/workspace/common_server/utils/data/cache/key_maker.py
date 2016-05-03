#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-19

@author: Jay
"""
import uuid

TOKEN_USER = 'TOKEN_TO_USER'     # token对应的用户名
USER_TOKEN = "USER_TO_TOKEN"     # 用户名对应的token
NAME_USER = "NAME_TO_USER"       # 用户名对应的用户信息


def mk_logic_key(*key_ls):
    """
    根据逻辑key类型，组合完整的key
    :param key_ls: key列表
    :return:
    """
    return ':'.join(unicode(v) for v in key_ls)


def mk_access_token():
    """
    产生access token
    """
    return uuid.uuid1().get_hex()

def ps_access_token(access_token):
    """
    解析access token
    """
    return access_token

def mk_username_token_key(user_name):
    """
    产生username 2 token的key
    :param user_name: 用户名
    :return:
    """
    return mk_logic_key(USER_TOKEN, user_name)

def mk_token_username_key(access_token):
    """
    产生token 2 username 的key
    :param access_token: 访问token
    :return:
    """
    return mk_logic_key(TOKEN_USER,
                        access_token)


def mk_name_user_key(user_name):
    """
    产生username 2 userinfo的key
    :param user_name:
    :return:
    """
    return mk_logic_key(NAME_USER, user_name)