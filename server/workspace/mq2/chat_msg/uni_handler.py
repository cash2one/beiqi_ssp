#coding:utf8
import traceback
from utils import logger
from mqtt_msg import mqtt_msg_bcast


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
    mqtt_msg_bcast(author, msg_body)




