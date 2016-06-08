#coding:utf8
import threading
from setting import *
from util.mqtt import MQTTClient
from utils import logger



class MqttInst(MQTTClient):
    def on_message(self, mqttc, userdata, msg):
        pass

GMqttClient = MqttInst()
GMqttClient.init(MQTT_HOST, MQTT_PORT)

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
    logger.debug('dev_msg handle_msg: packet: {0}'.format(packet))

    to_dev_sn = packet.pop('account')
    push_body = packet.pop('p')
    author = push_body.get('id')
    payload = push_body.get('description')

    topic = PUB_BEIQI_MSG_P2P.format(sn=to_dev_sn)
    logger.debug('dev_msg handle_msg mqtt: topic={0}, payload={1}'.format(topic, payload))
    GMqttClient.publish(topic, payload)

