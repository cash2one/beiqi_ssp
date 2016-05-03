#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-19

@author: Jay
"""


USER_TYPE_LS = [
    ADMIN_USER,                      # 管理员账户，可不用输入验证码
    CONTROLLER_USER,                 # 控制端账户，需要输入验证码
    DEVICE_USER,                     # 设备用户， 不需要输入验证码
    WECHAT_USER,                     # 微信用戶， 不需要輸入驗證碼
 ] = xrange(4)

NOT_VERIFY_CODE_USER_LS = [
    ADMIN_USER,
    DEVICE_USER,
    WECHAT_USER
]