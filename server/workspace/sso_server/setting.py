#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
SERVICE_TYPE = "s_sso_server"
VERSION = "0.0.1"

# MYSQL配置
DB_HOST = "192.168.2.192"
DB_PORT = 3306
DB_NAME = "beiqi_sso"
DB_USER = "system"
DB_PWD = "System"

# MYSQL 表格
DB_TBL_USER_INFO = 'user_info'
DB_TBL_DEVICE_INFO = 'device_info'
DB_TBL_GID_INFO = 'gid_info'
DB_TBL_SSP_USR_LOGIN = 'ssp_user_login'

# REDIS配置
ACC_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
DEV_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
MQ_DISP_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"

# LEVEL_DB 设置
LEVEL_DB_HOST = "127.0.0.1:25698"
