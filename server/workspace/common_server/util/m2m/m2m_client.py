#coding: utf-8

from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from tornado.iostream import IOStream
from tornado.stack_context import NullContext
import socket
from collections import deque
from m2m_encode import *


_RESP_FUTURE = 'future'
RESP_ERR = 'err'
RESP_RESULT = 'r'


class M2MClient(object):
    def __init__(self, server_addr=('61.177.97.2', 18585)):
        self.__svr_addr = server_addr
        self.__conn = None

    def register(self, term_id, imsi, vendor='beiqi', typ='pt30', version='1.0'):
        future = TracebackFuture()

        def handle_resp(resp):
            f = resp.get(_RESP_FUTURE) or future
            err = resp.get(RESP_ERR)
            result = resp.get(RESP_RESULT)

            if err:
                f.set_exception(err)
            else:
                f.set_result(result)

        with NullContext():
            if self.__conn is None or self.__conn.na():
                self.__conn = _M2MConn(handle_resp, self.__svr_addr)
                self.__conn.connect()
            self.__conn.write(future, term_id, imsi, vendor, typ, version)
        return future
        

sn = [0]


def incr_sn():
    """

    :rtype : int
    """
    global sn
    _ = sn[0]
    _ = 0 if 0xffff == _ else _ + 1
    sn[0] = _
    return _


class _M2MConn(object):
    def __init__(self, handle_resp, svr_addr):
        assert callable(handle_resp)
        self._io_loop = IOLoop.instance()
        
        self.__resp_cb = handle_resp
        self.__svr_addr = svr_addr
        self._stream = None
        self._send_buf = deque()
        self._recv_buf = ''
        self.__cmd_env = dict()
        self.__not_avail = False
        
    def na(self):
        """
        连接不可用
        """
        return self.__not_avail

    def connect(self):
        self._stream = IOStream(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0), io_loop=self._io_loop)
        self._stream.set_close_callback(self._on_close)
        self._stream.connect(self.__svr_addr, self._on_connect)
        
    def _on_connect(self):
        self._stream.set_nodelay(True)
        while len(self._send_buf) > 0:
            self._stream.write(self._send_buf.popleft())
        self._stream.read_until_close(self._last_closd_recv, self._on_recv)

    def close(self):
        self._stream.close_fd()

    def write(self, future, term_id, imsi, vendor, typ, version):
        sn = incr_sn()
        self.__cmd_env.update({sn: future})
        self._stream.write(m2m_register_req_encode(sn, term_id, imsi, vendor, typ, version))

    def _last_closd_recv(self, data):
        """
        socket关闭时最后几个字节
        """
        self._on_recv(data)

    def _on_recv(self, data):
        self._recv_buf = self._recv_buf + data
        while 1:
            if len(self._recv_buf) < 2:
                break

            total_len = decode_bits(self._recv_buf[:2], 2)
            if len(self._recv_buf) < total_len:
                break

            sn, result = m2m_register_rsp_decode(self._recv_buf[:total_len])
            f = self.__cmd_env.get(sn)
            if f is not None:
                #0: 注册成功
                #67: 重复注册
                self.__run_callback({_RESP_FUTURE: f, RESP_RESULT: result in (0, 67)})
                del self.__cmd_env[sn]
            else:
                print 'warn, sn not existed', sn
            self._recv_buf = self._recv_buf[total_len:]
            
    def __run_callback(self, resp):
        if self.__resp_cb is None:
            return
        self._io_loop.add_callback(self.__resp_cb, resp)            

    def _on_close(self):
        [self.__run_callback({_RESP_FUTURE: f, RESP_RESULT: False}) for f in self.__cmd_env.itervalues()]
        self.__cmd_env.clear()
        self.__not_avail = True
