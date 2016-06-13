#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-27

@author: Jay
"""
"""
MQTT 消息协议
"""

"""
CLIENT 2 SERVER
"""
C_PUB_ONLINE_REQ = 'node/online/{account}'
C_PUB_OFFLINE_REQ = 'node/offline/{account}'

S_SUB_ONLINE_REQ = 'node/online/+'
S_SUB_OFFLINE_REQ = 'node/offline/+'

"""
SERVER 2 CLIENT
"""
S_PUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/{gid}"
S_PUB_BEIQI_MSG_P2P = "BEIQI_MSG_P2P/{sn}"


C_SUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/{gid}"
C_SUB_BEIQI_MSG_P2P = "BEIQI_MSG_P2P/{sn}"
