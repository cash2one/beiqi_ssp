#coding:utf8
from mqtt_msg import *
from util.user import get_user_gids
from interfaces.mqtt_server.http_rpc import beiqi_msg_bcast
from setting import MQTT_SERVER_IP, MQTT_SERVER_PORT


def handle_msg(packet):
    """
    account为空时，推送给所有人
    :param packet:
    :return:
    """
    logger.debug('chat_msg handle_msg: packet: {0}'.format(packet))

    push_body = packet.pop('p', None)
    author = push_body.get('id')
    msg_body = push_body.get('description')

    gid_list = get_user_gids(author)
    logger.debug('mqtt_msg_bcast: gid_list=%r, author=%r, payload:%r', gid_list, author, msg_body)

    [beiqi_msg_bcast(MQTT_SERVER_IP, gid, msg_body,port=MQTT_SERVER_PORT) for gid in gid_list]




