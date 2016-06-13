#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-7

@author: Jay
"""
from util.convert import resolve_redis_url


# 排除参与测试的模块
excluded_dirs = ["utest_pandora", "utest_server_mgr"]

SYNC_WAIT_TIME = 3


SERVER_IP = "192.168.2.165"

SSO_SERVER_PORT = 8104
FILE_SERVER_PORT = 8106
VOICE_SERVER_PORT = 8200
DEV_SERVER_PORT = 8302
LOC_SERVER_PORT = 8202
PANDORA_SERVER_PORT = 20000

VOICE_SERVER_IP = "192.168.2.188"


TEST_USER_NAME = "18610060484@jiashu.com"
TEST_PASSWD = "416666"

TEST_SN = "P081101551000002"


# REDIS配置
ACC_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
CALC_RDS_URI = "redis://192.168.2.192:6379/1?pwd=123456"
DEV_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
MQ_DISP_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"


REDIS_IP, REDIS_PORT, _, REDIS_PASSWD = resolve_redis_url(ACC_RDS_URI)

#  MQTT
MQTT_IP = "192.168.2.188"
MQTT_PORT = 1883
