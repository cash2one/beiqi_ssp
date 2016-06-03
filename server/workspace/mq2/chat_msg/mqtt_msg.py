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
from util.user import get_user_gids
from util.mqtt import MQTTClient
from ios_msg import msg_2_ios
from wechat_msg import msg_2_wechat
from util.share import mk_share_file
from setting import *


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


def mqtt_msg_bcast(user, msg):
    """
    微信用户消息广播到客户端
    :param mqtt_client:mqtt客户端
    :param user: 微信用户
    :param msg: 需要发送的消息
    :return:
    """
    gid_list = get_user_gids(user)
    logger.debug('mqtt_msg_bcast: gid_list=%r, author=%r, payload:%r', gid_list, user, msg)
    [GMqttClient.publish(PUB_BEIQI_MSG_BCAST.format(gid), msg) for gid in gid_list]
