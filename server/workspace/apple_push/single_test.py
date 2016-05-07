#coding:utf-8

from tornado.ioloop import IOLoop
from tornado.gen import coroutine
from core import APNsClient
from util.stream_config_client import load as conf_load
import time
from encoding import v2_encode
from util.convert import parse_ip_port


compile_type = 'dev'
bundle_id = 'com.beiqi.helpers'

conf = dict(conf_load('apns.ini')).get('apns.ini')
section = ':'.join((compile_type, bundle_id))
cert_fn = conf.get(section, 'cert')


def run():
    device_token = 'fe9ffe531afbab4f8f44cf220de67e9c39ddf45874eaaa90559426d002f56a91'
    device_token = '3f24b320810a1ee6de177f2362f7fb6706a84b92e30a1182ee77443d239c634e'
    apns_client = APNsClient(cert_fn, parse_ip_port(conf.get('_apns', compile_type)), v2_encode)
    for i in xrange(10):
        print 'i = ', i
        apns_client.queue_push(device_token, {
            'aps': {
                'alert': 'hello tornado push' + str(i),
                'badge': 1,
                'sound': 'Voicemail.caf'
            }
        })


if __name__ == '__main__':
    loop = IOLoop.instance()
    loop.add_callback(run)
    loop.start()
