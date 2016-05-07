#coding:utf8
import threading
import urllib
import traceback
from utils import logger
from wechat2client import client_2_wechat_msg, wechat_2_client_msg
from setting import *
from . import MQTTClient
from util.convert import bs2utf8


def is_wechat_user(user):
    return user[:3] == 'wx#'


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
            author,  ftype, fn, ref, thumb_fn, thumb_ref, text = [bs2utf8(urllib.unquote(v)) for v in msg.payload.split(":")]
            logger.debug('MqttInst::on_message: author={0}, ftype={1}'.format(author, ftype))
            client_2_wechat_msg(author, ftype, fn, ref, thumb_fn, thumb_ref, text)
        except:
            logger.error('MqttInst::on_message parser error : payload={0}, tarce={1}'.format(msg.payload, traceback.format_exc()))

GMqttClient = MqttInst()
GMqttClient.init(MQTT_HOST, MQTT_PORT)
GMqttClient.subscribe(SUB_BEIQI_MSG_BCAST)

# 启动mqtt线程
mqtt_thread = threading.Thread(target=GMqttClient.start)
mqtt_thread.setDaemon(True)
mqtt_thread.start()


def handle_msg(packet):
    """
    account为空时，推送给所有人
    :param packet:
    :return:
    """
    logger.debug('wechat_msg handle_msg: packet: {0}'.format(packet))

    push_body = packet.pop('p', None)
    author = push_body.get('id')
    msg_body = push_body.get('description')

    wechat_2_client_msg(GMqttClient, author, msg_body)


