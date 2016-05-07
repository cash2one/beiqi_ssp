# coding:utf-8

import time
import socket
import ssl
from datetime import timedelta
from functools import partial
from binascii import a2b_hex
from collections import deque
from os import path
from encoding import err_resp, resp_errno
from utils import logger
from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from tornado.iostream import IOStream, SSLIOStream
from tornado.stack_context import NullContext


#证书根目录
CERT_ROOT = './certs'
#每秒检查错误应答
CHECK_TIMESPAN = 1
#每次取队列的上限
QUEUE_CAPACITY = 20
#重新创建连接间隔，单位秒
RENEW_CONN_TS = 600


def clear_connection(conn):
    logger.debug('closing conn: %x' % id(conn))
    conn.force_close()


class APNsClient(object):
    def __init__(self, cert_fn, server_tuple, encode_func):
        """
        1. 当read超时以至于断开时，从连接对象中获取上次未发完的缓存，清理该对象，重新创建连接对象
        2. 同时给每个连接对象设置5分钟的失效时间，到点自动清理该对象，重新创建
        :param encode_func: 编码函数，v1&v2的区别由外部解决
        """
        self.__conf = cert_fn, server_tuple, encode_func
        self.__conn = None

    def queue_push(self, device_token, payload):
        """
        时序内部对msg_id做映射，仅v1&v2协议格式支持错误应答

        :param device_token: 设备apns token
        :param payload: 包文dict
        """
        with NullContext():
            #多次对象拷贝
            legacy_buffers = None if self.__conn is None else self.__conn.sending_buffer[:]
            if self.__conn is None or self.__conn.critical:
                #不判定connected状态，因为该函数调用过快时，连接还未成功，导致前一个conn对象直接被gc回收
                #critical变量只有在read异常时设置
                self.__conn = _APNConn(legacy_buffers, *self.__conf)
                logger.debug('new conn: %x' % id(self.__conn))
                IOLoop.instance().add_timeout(
                    timedelta(seconds=RENEW_CONN_TS),
                    partial(clear_connection, self.__conn)
                )
                self.__conn.connect()
            self.__conn.append(device_token, payload)


class _APNConn(object):
    def __init__(self, prev_buffers, cert_file, svr_tuple, encode_func):
        """
        :param cert_file: 证书文件路径
        :param prev_buffers: 之前残留的推送链表

        按照苹果的尿性推送协议
        谁也不知道到底有没有成功
        FUCK JOBS!
        """
        self.__io_loop = IOLoop.instance()
        self.__cert = path.join(CERT_ROOT, cert_file)
        self.__svr_addr = svr_tuple
        self.__encode_func = encode_func

        self.__stream = None
        self.__connected = False
        #list自身的索引作为
        self.sending_buffer = []
        if prev_buffers and isinstance(prev_buffers, (list, tuple)):
            self.sending_buffer.extend(prev_buffers)

        self.__recv_buf = ''
        self.__connection_close_ts = None
        #从read读到的错误消息id，便于
        self.__recv_err_msgid = None
        self.critical = False

    def force_close(self):
        self.__connected = False
        self.__stream.close_fd()
        self.__stream = None
        self.critical = True

    def connect(self):
        self.__stream = SSLIOStream(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0),
            io_loop=self.__io_loop,
            ssl_options={
                'ssl_version': ssl.PROTOCOL_TLSv1,
                # 'ca_certs': path.join(CERT_ROOT, 'entrust_root_ca.pem'),
                'certfile': self.__cert,
                # 'cert_reqs': ssl.CERT_REQUIRED
            }
        )
        self.__stream.set_close_callback(self._on_close)
        self.__stream.connect(self.__svr_addr, self.__on_connect)

    def __on_connect(self):
        self.__connected = True
        self.__stream.set_nodelay(True)
        self.__stream.read_until_close(self._last_closd_recv, self._on_recv)
        self.__send_batch()

    def __do_check(self, sent_len):
        if self.__recv_err_msgid:
            logger.debug('CHECK: %r' % self.__recv_err_msgid)

        if self.__recv_err_msgid is None:
            self.sending_buffer = self.sending_buffer[sent_len:]
            self.__send_batch()
            return

        self.sending_buffer = self.sending_buffer[self.__recv_err_msgid:]
        self.__recv_err_msgid = None
        self.__stream.close_fd()
        self.__stream = None
        self.critical = True

    def __send_batch(self):
        """
        连接断开后就停了
        """
        if not self.__connected:
            return
        if not self.__stream:
            return
        l = self.sending_buffer[:QUEUE_CAPACITY]
        for i, b in enumerate(l):
            self.__stream.write(self.__encode_func(i, *b))
            logger.debug('>> %d - %s' % (i, b))
        self.__io_loop.add_timeout(timedelta(seconds=CHECK_TIMESPAN), partial(self.__do_check, len(l)))

    def append(self, device_token, payload):
        """
        :param device_token: app从apns服务器获取的64字节串
        :param payload: 报文dict
        """
        self.sending_buffer.append((device_token, payload))

    def _last_closd_recv(self, buf):
        """
        socket关闭时最后几个字节
        """
        if not buf:
            return
        self._on_recv(buf)

    def _on_recv(self, buf):
        logger.debug('<< %r' % buf)
        self.__recv_buf = self.__recv_buf + buf
        _ = err_resp(self.__recv_buf)
        if _ is None:
            return
        self.__recv_buf = ''
        errno, self.__recv_err_msgid = _
        logger.fatal('apns err: %d - %d - %s' % (self.__recv_err_msgid, errno, resp_errno.get(errno)))

    def _on_close(self):
        self.critical = True
        logger.warn('closed')
        self.__connected = False
        self.__stream = None