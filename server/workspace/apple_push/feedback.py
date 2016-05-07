#coding:utf-8


from util.convert import parse_ip_port
from core import APNsClient
from tornado.ioloop import IOLoop
from util.stream_config_client import load as conf_load


compile_type = 'inhouse'
bundle_id = 'SecurityWatch.beiqi.com.cn'

conf = dict(conf_load('apns.ini')).get('apns.ini')
section = ':'.join((compile_type, bundle_id))
cert_fn = conf.get(section, 'cert')
feedback_host = 'feedback.push.apple.com:2196'


def main():
    client = APNsClient(cert_fn, parse_ip_port(feedback_host), lambda *args: '')
    client.queue_push('04130e45d6ed9c3429e697e0cbce2ed2f5ac59868de95c281dc1dec83d07f631', '')


if __name__ == '__main__':
    loop = IOLoop.instance()
    loop.add_callback(main)
    loop.start()