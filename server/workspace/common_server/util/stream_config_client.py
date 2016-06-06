#coding:utf-8


import socket
from configx import conf_file
from utils import logger
from os import path


CONF_ROOT = './configs'


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
        logger.error('conf err: %s' % ex.strerror)
        yield ''


def load(*files):
    for f in files:
        yield f, conf_file(path.join(CONF_ROOT, f))


conf_load = load
