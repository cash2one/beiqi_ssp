#coding:utf-8
from utils import logger
from core import APNsClient
from encoding import v2_encode
from random import randint
import msgpack
from collections import defaultdict
from util.convert import parse_ip_port


APNS_CLIENT_PER_POOL = 10
APNS_CLIENT_TOP = APNS_CLIENT_PER_POOL - 1
apns_clients = defaultdict(list)


def queue_push(apns_conf, compile_type, bundle_id, device_token, push_body):
    push_body = msgpack.unpackb(push_body, encoding='utf-8')
    logger.debug('QUEUE: {0}, {1}, {2}, {3}'.format(compile_type, bundle_id, device_token, push_body))

    section = ':'.join((compile_type, bundle_id))

    dst_list = apns_clients.get(section)
    if not dst_list or len(dst_list) < APNS_CLIENT_PER_POOL:
        client = APNsClient(
            apns_conf.get(section, 'cert'),
            parse_ip_port(apns_conf.get('_apns', compile_type)),
            v2_encode)
        apns_clients[section].append(client)
    else:
        client = apns_clients[section][randint(0, APNS_CLIENT_TOP)]

    #从连接池中随机挑一个，或者创建一个新的
    client.queue_push(device_token, push_body)