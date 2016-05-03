#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-28

@author: Jay
"""

"""
SYSTEM ERROR CODE
"""

ERROR_SUCCESS = 0                           # 操作成功
ERROR_UNKNOWN_ERROR = 1                     # 未知错误
ERROR_PARAMS_ERROR = 2                      # 参数格式错误
ERROR_DB_ERROR = 3                          # 数据库操作错误
ERROR_ACCESS_TOKEN_ERROR = 4                # AccessToken错误
ERROR_VERIFY_CODE_ERROR = 5                 # 验证码错误
ERROR_SIGN_ERROR = 6                        # 参数签名出错
ERROR_SERVICE_START_ERROR = 7               # 服务器启动失败
ERROR_SERVICE_STOP_ERROR = 8                # 服务器关闭失败
ERROR_TIMEOUT = 9                           # 超时

"""
LOGIC ERROR CODE
"""
ERROR_OPER_NOT_PERMIT = 100                 # 操作不被允许,权限不够
ERROR_OPENFIRE_NEW_JID_FAIL = 101           # OPENFIRE 注册新JID失败
ERROR_USER_NAME_OR_PASSWORD_ERROR = 102     # 用户名或者密码错误
ERROR_USER_NAME_EXIST = 103                 # 用户名已经存在
ERROR_USER_NAME_NO_EXIST = 104              # 用户名不存在
ERROR_JID_OR_JID_PASS_ERROR = 105           # JID 获取JID 密码错误
ERROR_MXID = 106                            # MXID无效，没有JID，或者access_token过期
ERROR_JID_HAS_NOT_LOGIN = 107               # JID 还没有登录
ERROR_JID_ROSTER_UNSUBSCRIBE = 108          # JID 邀请添加roster被拒绝
ERROR_JID_ALREADY_IN_ROSTER = 109           # 被邀请者JID 已经在roster列表里面
ERROR_JID_NOT_IN_ROSTER = 110               # 被邀请者JID 不在被roster列表里面