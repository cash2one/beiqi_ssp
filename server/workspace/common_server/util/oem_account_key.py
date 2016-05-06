#coding:utf-8

import re
from convert import _cn_mobile_pat


COMMON_PATTERN = re.compile(r'^[_a-z\d]{6,16}$')

APP_KEY = 'aea8b32e091a11e681ee408d5c5a48ca'
APP_SECRET = 'b97326b0091a11e697ea408d5c5a48ca'
DEV_KEY = 'c289a8a1091a11e6a1a0408d5c5a48ca'
DEV_RC4 = 'db20ac11091a11e6ab0c408d5c5a48ca'
DEV_SECRET = 'cf1e06b0091a11e6ade7408d5c5a48ca'

beiqi_keys = {
    # 贝启
    APP_KEY: {
        's': APP_SECRET,
    },
    # 设备
    DEV_KEY: {
        'rc4_key': DEV_RC4,
        's': DEV_SECRET
    }
}




#s: secret
#p: 帐号格式
#f: 短信发送函数名称
#sms_prefix: 短信产品名
#sms_switch: 短信开关
#opt_mask: 权限覆盖，需求变更导致原始key不满足要求
#tr: 翻译语种


oem_accounts = {
    # 贝启
    APP_KEY: {
        's': APP_SECRET,
    },
}
