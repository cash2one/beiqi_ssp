#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-27

@author: Jay
"""
from utils.crypto.sign import Signer
from utils.service_control.finder import get_cur_ip
from utils.service_control.setting import SM_TCP_PORT

TCP_SIGN = Signer().gen_sign(get_cur_ip(), SM_TCP_PORT)
