#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/13

@author: Jay
"""
import threading
import traceback
import urllib2
from utils import logger
from util.mqtt import MQTTClient
from ios_msg import msg_2_ios
from wechat_msg import msg_2_wechat
from util.share import mk_share_file
from setting import *

"""
这里进行mqtt的消息接收，然后广播到ios（推送），wechat（客服接口）；
目前已经有替代的api接口/chat/bcast，但是android客户端还没有修改过来，后期统一采用api接口，mqtt只负责推送给客户端，不接收数据
"""


class MqttInst(MQTTClient):
    def on_message(self, mqttc, userdata, msg):
        """
        接收到mqtt服务器消息通知
        :param mqttc:
        :param userdata:
        :param msg:
        :return:
        """
        logger.debug('MqttInst::on_message: topic={0}, payload={1}'.format(msg.topic, msg.payload))
        try:
            author,  ftype, fn, ref, thumb_fn, thumb_ref, text = [urllib2.unquote(v) for v in msg.payload.split(":")]
            msg_2_ios(author, ftype, mk_share_file(fn, ref, thumb_fn, thumb_ref), text)
            msg_2_wechat(author, ftype, fn, ref, thumb_fn, thumb_ref, text)
        except:
            logger.error('MqttInst::on_message parser error : payload={0}, tarce={1}'.format(msg.payload, traceback.format_exc()))

GMqttClient = MqttInst()
GMqttClient.init(MQTT_HOST, MQTT_PORT)
GMqttClient.subscribe(SUB_BEIQI_MSG_BCAST)

# 启动mqtt线程
mqtt_thread = threading.Thread(target=GMqttClient.start)
mqtt_thread.setDaemon(True)
mqtt_thread.start()
