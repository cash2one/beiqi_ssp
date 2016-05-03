#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-17

@author: Jay
"""
from utils.crypto.sign import Signer
from utils.service_control.finder import get_cur_ip
from utils.service_control.parser import ArgumentParser

HTTP_SIGN = Signer().gen_sign(get_cur_ip(), ArgumentParser().args.http_port)
