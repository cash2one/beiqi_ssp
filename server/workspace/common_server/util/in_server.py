#coding:utf-8

import socket
import time
import struct
from tornado.tcpserver import TCPServer
from tornado import stack_context
from tornado.util import bytes_type
from redis.async_redis.redis_resp import decode_resp_ondemand
from utils import logger


class _BadRequestException(Exception):
    """Exception class for malformed HTTP requests."""
    pass


class IncomingServer(TCPServer):
    def __init__(self, req_cb, connected_reg=None, lost_reg=None, log=True, **kwargs):
        self.__req_cb = req_cb
        self.__con_reg = connected_reg
        self.__lost_reg = lost_reg
        self.__log = log
        super(IncomingServer, self).__init__(**kwargs)

    def handle_stream(self, stream, address):
        c = ProxyCon(stream, address, self.__req_cb, self.__lost_reg, self.__log)
        if self.__con_reg is not None:
            self.__con_reg(c)


class ProxyCon(object):
    def __init__(self, stream, address, request_callback, lost_reg, log):
        self.__req = None
        self.__log = log
        self.__req_done = False
        self.__write_cb = None
        self.__close_cb = None
        self.__lost_reg = lost_reg

        self.stream = stream
        self.address = address

        self.address_family = stream.socket.family
        self.request_callback = request_callback

        self._clear_request_state()
        self._header_callback = stack_context.wrap(self._on_index)
        self.stream.set_close_callback(self._on_connection_close)
        self.stream.read_bytes(6, self._header_callback)

    def _clear_request_state(self):
        self.__req = None
        self.__req_done = False
        self.__write_cb = None
        self.__close_cb = None

    def set_close_callback(self, callback):
        self.__close_cb = stack_context.wrap(callback)

    def _on_connection_close(self):
        if self.__close_cb is not None:
            callback = self.__close_cb
            self.__close_cb = None
            callback()
        self._header_callback = None
        self._clear_request_state()
        if self.__lost_reg:
            self.__lost_reg(self)

    def close(self):
        if self.__log:
            logger.debug('CLOSED: {0}'.format(self.address))

        self.stream.close()
        self._header_callback = None
        self._clear_request_state()

    def write(self, chunk, callback=None):
        if not self.stream.closed():
            self.__write_cb = stack_context.wrap(callback)
            self.stream.write(chunk, self._on_write_complete)

    def finish(self):
        self.__req_done = True
        self.stream.set_nodelay(True)
        if not self.stream.writing():
            self._finish_request()

    def _on_write_complete(self):
        if self.__write_cb is not None:
            callback = self.__write_cb
            self.__write_cb = None
            callback()
        if self.__req_done and not self.stream.writing():
            self._finish_request()

    def _finish_request(self):
        self._clear_request_state()
        try:
            self.stream.read_bytes(6, self._header_callback)
            self.stream.set_nodelay(False)
        except IOError, ex:
            logger.error('io err: {0}'.format(ex))
            self.close()

    def _on_index(self, data):
        if self.__log:
            logger.debug('>> INDEX: %r' % data)

        if not data.startswith('*1'):
            #判定版本
            logger.warn('index malformat: %r' % data)
            self.close()
            return

        payload_len = struct.unpack('>I', data[2:6])[0]
        remote_ip = self.address[0] if self.address_family in (socket.AF_INET, socket.AF_INET6) else '0.0.0.0'

        self.__req = PushRequest(remote_ip, self)
        self.stream.read_bytes(payload_len, self._on_request_body)

    def _on_request_body(self, data):
        if self.__log:
            logger.debug('>> PAYLOAD: %r' % data)
        ok, parsed, remain = decode_resp_ondemand(data, 0, False, 1)
        if not ok or remain or not parsed:
            #命令字，序号
            logger.warn('invalid body: %r' % data)
            self.close()
            return

        self.__req.args = parsed
        self.request_callback(self.__req)


class PushRequest(object):
    def __init__(self, remote_ip, connection):
        self.remote_ip = remote_ip
        self.connection = connection
        self._start_time = time.time()
        self._finish_time = None

    def write(self, chunk, callback=None):
        assert isinstance(chunk, bytes_type)
        self.connection.write(chunk, callback=callback)

    def finish(self):
        self.connection.finish()
        self._finish_time = time.time()

    def request_time(self):
        if self._finish_time is None:
            return time.time() - self._start_time
        return self._finish_time - self._start_time