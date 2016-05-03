#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-18

@author: Jay
"""
import urllib

APPID = "wx361fd33e509893b1"
APPSECRET = "bdb9fd24335e639516655ad1d075be28"

TOKEN = "zghl"
ENCODING_AES_KEY = "zghlzghlzghlzghlzghlzghlzghlzghlzghlzghlzgh"


API_WECHAT_DOMAIN = "api.weixin.qq.com"
OPEN_WECHAT_DOMAIN = "open.weixin.qq.com"

CLIENT_ACCESS_TOKEN_URL = "https://%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" \
                          % (API_WECHAT_DOMAIN, APPID, APPSECRET)


MENU_CREATE_URL = lambda access_token: "https://%s/cgi-bin/menu/create?access_token=%s" % (API_WECHAT_DOMAIN, access_token)
MENU_GET_URL = lambda access_token: "https://%s/cgi-bin/menu/get?access_token=%s" % (API_WECHAT_DOMAIN, access_token)


UAUTH_ACCESSS_TOKEN_URL = lambda code: "https://%s/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" \
                                       % (API_WECHAT_DOMAIN, APPID, APPSECRET, code)



WECHAT_MSG_TYPE =[
    WCMT_TEXT,
    WCMT_IMAGE,
    WCMT_VOICE,
    WCMT_VIDEO,
    WCMT_LOCATION,
    WCMT_LINK,
    WCMT_EVENT,
] = [
    "text",
    "image",
    "voice",
    "video",
    "location",
    "link",
    "event"
]

WECHAT_EVENT_TYPE = [
    WCET_SUBSCRIBE,
    WCET_UNSUBSCRIBE,
    WCET_SCANCODE_WAITMSG,
    WCET_SCANCODE_PUSH,
    WCET_VIEW,
    WCET_CLICK,
] = [
    "subscribe",
    "unsubscribe",
    "scancode_waitmsg",
    "scancode_push",
    "VIEW",
    "CLICK",
]

WECHAT_EVENT_KEY = [
    WCEK_SCANCODE_BANDING_DEVICE,
] = [
    "scancode_banding_device",
]

GEN_WECHAT_REDIRECT_URL = lambda redirect_url, response_type="code", scope="snsapi_base", state=1: \
    "https://%s/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect" %\
    (OPEN_WECHAT_DOMAIN,
     APPID,
     urllib.quote(redirect_url, safe=""),
     response_type,
     scope,
     state)
