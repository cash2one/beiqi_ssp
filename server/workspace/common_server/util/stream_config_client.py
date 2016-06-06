#coding:utf-8
import os
import sys
import socket
from configx import conf_file
from utils import logger
from os import path

# configs文件位于启动脚本的configs同级目录下
CONF_ROOT = os.path.join(os.path.dirname(sys.argv[0]), "configs")


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
