#coding:utf-8


import socket
from internal_forward.conf_encode import encode
from configx import conf_file, conf_stream
from convert import parse_ip_port
from redis.async_redis.redis_resp import decode_resp_ondemand
from log_util import gen_log
from itertools import izip
from os import path


CONF_ROOT = './configs'
CONFIG_SERVER_HOST = conf_file('./configs/sentinel.ini').get('default', 'host')


def _create_sock(host):
    s = socket.socket()
    s.setblocking(True)
    s.settimeout(.5)
    try:
        s.connect(host)
        return s
    except socket.error:
        s.close()
        return None


def _send_recv(sock, out_buf):
    try:
        sock.send(out_buf)
        while 1:
            yield sock.recv(1024)
    except socket.timeout:
        #正常退出
        yield ''
    except socket.error, ex:
        gen_log.error('conf err: %s' % ex.strerror)
        yield ''


def load(*files):
    sock = _create_sock(parse_ip_port(CONFIG_SERVER_HOST))
    if not sock:
        for f in files:
            yield f, conf_file(path.join(CONF_ROOT, f))
        return

    s = ''.join(_send_recv(sock, encode(*files)))
    sock.close()
    if s:
        ok, resp, remain = decode_resp_ondemand(s, 0, 0, 1)
        for k, v in izip(resp[::2], resp[1::2]):
            yield k, conf_stream(v)
        return
    for f in files:
        yield f, conf_file(path.join(CONF_ROOT, f))


conf_load = load