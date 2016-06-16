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
DB_TBL_USER_INFO = 'beiqi_api.user_info'
DB_TBL_DEVICE_INFO = 'beiqi_dev.device_info'
DB_TBL_ETICKET = "beiqi_api.eticket"
DB_TBL_RES_CLS = "beiqi_api.res_cls"
DB_TBL_RES_ALBUM = "beiqi_api.res_album"
DB_TBL_RESOURCE = "beiqi_api.resource"


# 每页显示的数量
PAGE_COUNT = 500

# REDIS配置
ACC_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
CALC_RDS_URI = "redis://192.168.2.192:6379/1?pwd=123456"
DEV_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"
MQ_DISP_RDS_URI = "redis://192.168.2.192:6379/0?pwd=123456"


BEIQI_FILE_DOWN_URL = 'http://localhost:8106/down?'
BEIQI_FILE_DELETE_URL = 'http://localhost:8106/delete_file?{file}'
WECHAT_COMMENT_PAGE_URL = "http://localhost:8108/wechat/pages/comment?"
