#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
SERVICE_TYPE = "s_dev_server"
VERSION = "0.0.1"

# MYSQL配置
DB_HOST = "beiqissp.cv38u3dpqyx2.ap-southeast-1.rds.amazonaws.com"
DB_PORT = 3306
DB_NAME = "beiqi_dev"
DB_USER = "system"
DB_PWD = "MySystem"

# MYSQL 表格
DB_TBL_DEVICE_INFO = 'device_info'
DB_TBL_GID_INFO = 'gid_info'
DB_TBL_LOCATION = 'location'
DB_TBL_DEV_STATE = 'dev_state'

# REDIS配置
ACC_RDS_URI = "redis://54.169.67.124:6379/0?pwd=123456"
CALC_RDS_URI = "redis://54.169.67.124:6379/1?pwd=123456"
DEV_RDS_URI = "redis://54.169.67.124:6379/2?pwd=123456"
MQ_DISP_RDS_URI = "redis://54.169.67.124:6379/3?pwd=123456"

# LEVEL_DB 设置
LEVEL_DB_HOST = "127.0.0.1:25698"
