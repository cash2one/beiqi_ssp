#coding:utf-8


from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from tornado.iostream import IOStream
from tornado.stack_context import NullContext
import socket
from collections import deque
from util.redis.async_redis.redis_resp import decode_resp_ondemand
from utils import logger


_RESP_FUTURE = 'future'
RESP_ERR = 'err'
RESP_RESULT = 'r'


class GeneralInternalClient(object):
    """
    服务器回包必须也用redis格式编码
    """
    def __init__(self, server_addr):
        self.__svr_addr = server_addr
        self.__conn = None

    def forward(self, encode_result):
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
            if self.__conn is None or not self.__conn.con_ok():
                self.__conn = _PrxConn(handle_resp, self.__svr_addr)
                self.__conn.connect()
            self.__conn.write(future, encode_result)
        return future


class _PrxConn(object):
    def __init__(self, handle_resp, svr_addr):
        assert callable(handle_resp)
        self._io_loop = IOLoop.instance()

        self.__resp_cb = handle_resp
        self.__svr_addr = svr_addr
        self._stream = None
        self._send_buf = deque()
        self._recv_buf = ''
        self.__cmd_env = deque()
        self.__con_ok = False

    def con_ok(self):
        """
        连接不可用
        """
        return self.__con_ok

    def connect(self):
        self._stream = IOStream(socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0), io_loop=self._io_loop)
        self._stream.set_close_callback(self._on_close)
        self._stream.connect(self.__svr_addr, self._on_connect)

    def _on_connect(self):
        self._stream.set_nodelay(True)
        while len(self._send_buf) > 0:
            self._stream.write(self._send_buf.popleft())
        self._stream.read_until_close(self._last_closd_recv, self._on_recv)
        self.__con_ok = True

    def write(self, future, encode_result):
        self.__cmd_env.append(future)
        if not self.__con_ok:
            self._send_buf.append(encode_result)
        else:
            self._stream.write(encode_result)

    def _last_closd_recv(self, data):
        """
        socket关闭时最后几个字节
        """
        self._on_recv(data)

    def _on_recv(self, buf):
        self._recv_buf += buf
        while 1:
            if not self._recv_buf:
                break
            ok, payload, self._recv_buf = decode_resp_ondemand(self._recv_buf, 0, False, 1)
            if not ok:
                break
            if payload and isinstance(payload, (list, tuple)) and 1 == len(payload):
                payload = payload[0]
            self.__run_callback({_RESP_FUTURE: self.__cmd_env.popleft(), RESP_RESULT: payload})

    def __run_callback(self, resp):
        if self.__resp_cb is None:
            return
        self._io_loop.add_callback(self.__resp_cb, resp)

    def _on_close(self):
        self.__con_ok = False
        while len(self.__cmd_env) > 0:
            self.__run_callback({_RESP_FUTURE: self.__cmd_env.popleft(), RESP_RESULT: 0})
        self.__cmd_env.clear()
