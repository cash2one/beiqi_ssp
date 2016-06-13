#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
import time
from utils import logger
from utils.wapper.catch import except_adaptor
from utils.wapper.mqtt import mqtt_subscribe_decorator
from mqtt_server.common import opcode
from mqtt_server.apps.mqtt_app import MQTT_APP
from util.redis_cmds.mqtt import set_mqtt_status
from mqtt_server.config import GDevRdsInts


@mqtt_subscribe_decorator(MQTT_APP(), opcode.S_SUB_ONLINE_REQ)
@except_adaptor()
def mqtt_online_req(mqttc, userdata, topic, payload):
    """
    设备上线请求
    :param mqttc:请求客户端
    :param userdata:
    :param topic:主题
    :param payload:内容
    :return:
    """
    topic, acc = topic.rsplit('/', 1)
    status = 'online' + ':' + str(time.time())
    logger.debug('mqtt_online_req:topic = %r, acc = %r, payload = %r', topic, acc, payload)
    GDevRdsInts.send_cmd(*set_mqtt_status(acc, status))


@mqtt_subscribe_decorator(MQTT_APP(), opcode.S_SUB_OFFLINE_REQ)
@except_adaptor()
def mqtt_offline_req(mqttc, userdata, topic, payload):
    """
    设备下线请求
    :param mqttc:请求客户端
    :param userdata:
    :param topic:主题
    :param payload:内容
    :return:
    """
    topic, acc = topic.rsplit('/', 1)
    status = 'offline' + ':' + str(time.time())
    logger.debug('mqtt_offline_req:topic = %r, acc = %r, payload = %r', topic, acc, payload)
    GDevRdsInts.send_cmd(*set_mqtt_status(acc, status))