#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
SERVICE_TYPE = "s_api_server"
VERSION = "0.0.1"

# MYSQL配置
DB_HOST = "192.168.2.192"
DB_PORT = 3306
DB_NAME = "beiqi_ssp"
DB_USER = "system"
DB_PWD = "System"

# REDIS配置
ACC_RDS_URI = "redis://127.0.0.1:7000/0?pwd=beiqiredisadmin@002"
CALC_RDS_URI = "redis://127.0.0.1:7300/1?pwd=beiqiredisadmin@002"
DEV_RDS_URI = "redis://127.0.0.1:7100/0?pwd=beiqiredisadmin@002"
MQ_DISP_RDS_URI = "redis://localhost:7400/0?pwd=beiqiredisadmin@002"

# LEVEL_DB 设置
LEVEL_DB_HOST = "127.0.0.1:25698"
