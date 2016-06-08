#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-4

@author: Jay
"""
from utils.network.http import HttpRpcClient
from beiqissp_test.setting import SERVER_IP

SSOHttpRpcClt = HttpRpcClient(SERVER_IP, 8104)