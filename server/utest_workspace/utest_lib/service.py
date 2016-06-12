#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-4

@author: Jay
"""
from utils.network.http import HttpRpcClient
from utest_lib.setting import SERVER_IP

SSO_SERVER_PORT = 8104
FILE_SERVER_PORT = 8106
SSOHttpRpcClt = HttpRpcClient(SERVER_IP, SSO_SERVER_PORT)
FileSvrHttpRpcClt = HttpRpcClient(SERVER_IP, FILE_SERVER_PORT)