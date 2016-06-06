#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
SERVICE_TYPE = "s_wechat_server"
VERSION = "0.0.1"

# REDIS配置
ACC_RDS_URI = "redis://54.169.67.124:6379/0?pwd=123456"
DEV_RDS_URI = "redis://54.169.67.124:6379/2?pwd=123456"
MQ_DISP_RDS_URI = "redis://54.169.67.124:6379/3?pwd=123456"

# MYSQL 表格
DB_TBL_USER_INFO = 'user_info'


APPID = 'wxd0334fe5bbc270d2'
APPSECRET = '6d2f605d568f6a66f2acd6736befa8e3'

TOKEN = 'beiqiwechattoken'

BEIQI_FILE_UP_URL = 'http://localhost:8106/up?'
WX_MEDIA_DOWN_URL = 'http://file.api.weixin.qq.com/cgi-bin/media/get?access_token={0}&media_id={1}'
WX_USERINFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN'

WX_GET_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(APPID, APPSECRET)
WX_GET_TICKER_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token={access_token}'


WECHAT_SERACH_DEVICE="http://wechatapi.beiqicloud.com:8108/wechat/pages/search_device"

