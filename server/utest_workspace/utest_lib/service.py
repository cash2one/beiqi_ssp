#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-4

@author: Jay
"""
from utils.network.http import HttpRpcClient
from util.redis.redis_client import Redis
from utest_lib.setting import *


# service
SSOHttpRpcClt = HttpRpcClient(SERVER_IP, SSO_SERVER_PORT)
FileSvrHttpRpcClt = HttpRpcClient(SERVER_IP, FILE_SERVER_PORT)
VoiceSvrHttpRpcClt = HttpRpcClient(VOICE_SERVER_IP, VOICE_SERVER_PORT)


# redis
GCalcRdsInts = Redis(ACC_RDS_URI)