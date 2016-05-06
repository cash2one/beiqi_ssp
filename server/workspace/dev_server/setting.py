#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
SERVICE_TYPE = "s_dev_server"
VERSION = "0.0.1"

# MYSQL配置
DB_HOST = "192.168.2.192"
DB_PORT = 3306
DB_NAME = "beiqi_ssp"
DB_USER = "system"
DB_PWD = "System"

# REDIS配置
ACC_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
CALC_RDS_URI = "redis://192.168.2.192:6379/1?pwd=123456"
DEV_RDS_URI = "redis://192.168.2.192:6379/2?pwd=123456"
MQ_DISP_RDS_URI = "redis://192.168.2.192:6379/3?pwd=123456"

# LEVEL_DB 设置
LEVEL_DB_HOST = "127.0.0.1:25698"
