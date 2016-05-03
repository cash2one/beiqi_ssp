#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-25

@author: Jay
"""
import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub
from utils.wapper.stackless import gevent_adaptor
from utils.wapper.catch import except_adaptor
from utils import logger
from utils.service_control.setting import PT_MQTT
from utils.wapper.mqtt import mqtt_publish_decorator, mqtt_onmessage_decorator

class MQTTCallback(object):
    """
    MQTT 回调处理
    """
    def __init__(self):
        self.topic_to_fun_dic = {}

    def on_connect(self, mqttc, userdata, flags, rc):
        """
        连接mqtt服务器成功通知
        :param mqttc:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        pass
        #logger.info("MQTTCallback::on_connect, mqttc:%s, userdata:%s, flags:%s, rc:%s" % (self, userdata, flags, rc))

    def on_disconnect(self, mqttc, userdata, rc):
        """
        断开mqtt服务器连接通知
        :param mqttc:
        :param userdata:
        :param rc:
        :return:
        """
        pass
        #logger.info("MQTTCallback::on_disconnect, mqttc:%s, userdata:%s, rc:%s" % (self, userdata, rc))

    @except_adaptor(is_raise=False)
    @mqtt_onmessage_decorator()
    def on_message(self, mqttc, userdata, msg):
        """
        接收到mqtt服务器消息通知
        :param mqttc:
        :param userdata:
        :param msg:
        :return:
        """
        self._on_message(mqttc, userdata, msg)

    def _on_message(self, mqttc, userdata, msg):
        """
        接收消息处理
        :param mqttc:
        :param userdata:
        :param msg:
        :return:
        """
        #logger.info("MQTTCallback::on_message, mqttc:%s, userdata:%s, topic:%s, payload:%s" % (self, userdata, msg.topic, msg.payload))
        [handle_fun(self, userdata=userdata, topic=msg.topic, payload=msg.payload)
         for sub, handle_fun in self.topic_to_fun_dic.items()
         if topic_matches_sub(sub, msg.topic)]
        return True

    def on_publish(self, mqttc, userdata, mid):
        """
        消息成功发布到mqtt服务器通知
        :param mqttc:
        :param userdata:
        :param mid:
        :return:
        """
        pass
        #logger.info("MQTTCallback::on_publish, mqttc:%s, userdata:%s, mid:%s" % (self, userdata, mid))

    def on_subscribe(self, mqttc, userdata, mid, granted_qos):
        """
        成功从mqtt服务器预定消息通知
        :param mqttc:
        :param userdata:
        :param mid:
        :param granted_qos:
        :return:
        """
        pass
        #logger.info("MQTTCallback::on_subscribe: mqttc:%s, userdata:%s, mid:%s, granted_qos:%s" % (self, userdata, mid, granted_qos))

    def on_log(self, mqttc, userdata, level, string):
        """
        日志通知
        :param mqttc:
        :param userdata:
        :param level:
        :param string:
        :return:
        """
        pass
        #logger.info("MQTTCallback::on_log: mqttc:%s, userdata:%s, level:%s, string:%s" % (self, userdata, level, string))


class MQTTClient(MQTTCallback):
    """
    MQTT客户端
    """
    def __init__(self, clientid=None):
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect

        super(MQTTClient, self).__init__()
        self.protocol = PT_MQTT

    def init(self, host, port=1883):
        """
        mqtt初始化
        :param host: 主机
        :param port: 端口
        :return:
        """
        self.host = host
        self.port = port
        self._mqttc.connect(host, port, 60)

    @gevent_adaptor(use_join_result=False)
    def start(self):
        """
        服务开启
        :return:
        """
        logger.warn("start listen on %s:%s" % (self.protocol, self.port))
        self._mqttc.loop_forever()

    @gevent_adaptor(use_join_result=False)
    def stop(self):
        """
        服务停止
        :return:
        """
        self._mqttc.disconnect()

    @gevent_adaptor(use_join_result=False)
    def username_pw_set(self, username, password=None):
        """
        设置用户名和密码
        :param username:
        :param password:
        :return:
        """
        self._mqttc.username_pw_set(username, password)

    @gevent_adaptor(use_join_result=False)
    def user_data_set(self, userdata):
        """
        设置用户数据
        :param userdata:
        :return:
        """
        self._mqttc.user_data_set(userdata)

    @mqtt_publish_decorator()
    @gevent_adaptor(use_join_result=False)
    def publish(self, topic, payload, qos=2, retain=False):
        """
        消息发布
        :param topic: 主题
        :param payload: 内容
        :param qos: qos
        :param retain:
        :return:
        """
        self._mqttc.publish(topic, payload, qos, retain)

    @gevent_adaptor(use_join_result=False)
    def subscribe(self, topic, hander_fun, qos=2):
        """
        消息预定
        :param topic: 主题
        :param hander_fun: 处理函数
        :param qos: qos
        :return:None
        """
        self.topic_to_fun_dic[topic] = hander_fun
        self._mqttc.subscribe(topic, qos)

    @gevent_adaptor(use_join_result=False)
    def unsubscribe(self, topic):
        """
        取消某个消息的预定
        :param topic: 主题
        :return:
        """
        self._mqttc.unsubscribe(topic)

