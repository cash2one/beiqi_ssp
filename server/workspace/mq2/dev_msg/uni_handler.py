#coding:utf8
from setting import *
from utils import logger
from interfaces.mqtt_server.http_rpc import beiqi_msg_p2p


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
    beiqi_msg_p2p(MQTT_SERVER_IP, to_dev_sn, payload, port=MQTT_SERVER_PORT)

