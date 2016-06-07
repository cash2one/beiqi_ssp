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
DB_NAME = "beiqi_api"
DB_USER = "system"
DB_PWD = "System"

# MYSQL 表格
DB_TBL_USER_INFO = 'user_info'
DB_TBL_DEVICE_INFO = 'device_info'
DB_TBL_ETICKET = "eticket"
DB_TBL_RES_CLS = "res_cls"
DB_TBL_RES_ALBUM = "res_album"
DB_TBL_RESOURCE = "resource"


# 每页显示的数量
PAGE_COUNT = 500

# REDIS配置
ACC_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
CALC_RDS_URI = "redis://192.168.2.192:6379/1?pwd=123456"
DEV_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
MQ_DISP_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"

# LEVEL_DB 设置
LEVEL_DB_HOST = "127.0.0.1:25698"


ssp_down_file_url = 'http://localhost:8106/down?'
wechat_comment_page_url = "http://localhost:8108/wechat/pages/comment?"
