#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
import os
from abc import ABCMeta
from utils.meta.singleton import Singleton
from utils.network.mqtt import MQTTClient
from utils.comm_func import import_handlers
from utils.wapper.stackless import gevent_adaptor
from utils.wapper.catch import except_adaptor
from utils.wapper.mqtt import mqtt_publish_decorator

singleton_abcmeta = type("singleton_abcmeta", (ABCMeta, Singleton), {})


class MQTT_APP(MQTTClient):
    """
    Mqtt服务
    """
    __metaclass__ = singleton_abcmeta

    def __init__(self, clientid=None):
        super(MQTT_APP, self).__init__(clientid)

    def init(self, host, port=1883):
        """
        mqtt初始化
        :param host: 主机
        :param port: 端口
        :return:
        """
        super(MQTT_APP, self).init(host, port)
        self.import_handlers()

    @mqtt_publish_decorator(use_json_dumps=False)
    @gevent_adaptor(use_join_result=False)
    def publish(self, topic, payload=None, qos=2, retain=False):
        """
        消息发布
        :param topic: 主题
        :param payload: 内容
        :param qos: qos
        :param retain:
        :return:
        """
        self._mqttc.publish(topic, payload, qos, retain)

    @except_adaptor(is_raise=False)
    def on_message(self, mqttc, userdata, msg):
        """
        接收到mqtt服务器消息通知
        :param mqttc:
        :param userdata:
        :param msg:
        :return:
        """
        self._on_message(mqttc, userdata, msg)

    @classmethod
    def import_handlers(cls):
        """
        导入mqtt接收handler
        :return:
        """
        # import handlers
        handler_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "logic", "mqtt", "handler")
        import_path = "mqtt_server.logic.mqtt.handler"
        import_handlers(handler_path, import_path)