#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
from mqtt_server.common.opcode import *

###########################################################
# cleint mqtt publish
###########################################################


def c_pub_online_req(mqttc, account):
    payload = account
    mqttc.publish(C_PUB_ONLINE_REQ.format(account=account), payload).join()


def c_pub_offline_req(mqttc, account):
    payload = account
    mqttc.publish(C_PUB_OFFLINE_REQ.format(account=account), payload).join()


###########################################################
# cleint mqtt subscribe
###########################################################


def c_sub_beiqi_msg_bacst(mqttc, gid, fun):
    mqttc.subscribe(C_SUB_BEIQI_MSG_BCAST.format(gid=gid), fun).join()


def c_sub_beiqi_msg_p2p(mqttc, sn, fun):
    mqttc.subscribe(S_PUB_BEIQI_MSG_P2P.format(sn=sn), fun).join()