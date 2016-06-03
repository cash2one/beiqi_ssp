#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/19

@author: Jay
"""

BEIQI_VOP_TOKEN = 'beiqi_vop_token'


def get_beiqi_vop_token():
    return 'get', BEIQI_VOP_TOKEN


def set_beiqi_vop_token(token, expires):
    return 'set', BEIQI_VOP_TOKEN, token, int(expires)

