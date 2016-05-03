#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-2

@author: Jay
"""
SM_HTTP_PORT = 16666
SM_TCP_PORT = 18888
SM_UDP_PORT = 16688

# 第三方服务标识头
TP_SERVICE_FLAG = "tp_"
SERVICE_FLAG = "s_"

def is_logic_service(service):
    return SERVICE_FLAG in service

def is_tp_service(service):
    return TP_SERVICE_FLAG in service

# 网络协议类型
PROTOCOL_TYPE = [
    PT_TCP,
    PT_UDP,
    PT_HTTP,
    PT_HTTPS,
    PT_XMPP,
    PT_WEB_SOCKET,
    PT_MQTT,
] = [
    "TCP",
    "UDP",
    "HTTP",
    "HTTPS",
    "XMPP",
    "WEB_SOCKET",
    "MQTT",
]

# 集群选择算法类型
RDM_TYPE = [
    RT_CPU_USAGE_RDM,       # 选择CPU使用率最低的一个服务，如果CPU使用率都一样，那么随机一个；无缓存数据的服务采用此算法
    RT_HASH_RING,           # 采用一致性hash算法进行选择;有缓存数据、状态数据的服务采用此算法
] = xrange(0, 2)

SERVICE_STATE = [
    SS_FREE,
    SS_RUNNING,
] = xrange(0, 2)