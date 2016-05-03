#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-25

@author: Jay
"""
from utils.wapper.stackless import gevent_adaptor
from utils import logger
PING_RESPONSE = "ping response!"


class RpcServer(object):
    """
    Rpc服务
    """
    def __init__(self, protocol, port, server):
        self.protocol = protocol
        self.port = port
        self.server = server

    @gevent_adaptor(use_join_result=False)
    def start(self):
        """
        服务开启
        :return:
        """
        assert self.server
        logger.warn("start listen on %s:%s" % (self.protocol, self.port))
        self.server.serve_forever()

    def stop(self):
        """
        服务关闭
        :return:
        """
        assert self.server
        self.server.stop()


class RpcClient(object):
    """
    Rpc客户端
    """
    def _rpc_fetch(self, *args, **kwargs):
        """
        rpc函数调用实现,需要继承者自己实现
        :param func_name:函数名
        :param args: 参数
        :return:函数调用结果
        """
        pass

    @gevent_adaptor()
    def fetch_async(self, func_name, *args):
        """
        协程非阻塞调用
        :param func_name:
        :param args:
        :return:
        """
        return self._rpc_fetch(func_name, *args)

    def fetch_sync(self, func_name, *args):
        """
        阻塞调用
        :param func_name:
        :param args:
        :return:
        """
        return self._rpc_fetch(func_name, *args)

    def ping(self):
        """
        ping 函数调用
        :return:
        """
        return self.fetch_sync("ping")

    def open(self):
        """
        打开连接，不处理，checker使用的时候兼容系统类
        :return:
        """
        return self

    def is_expired(self):
        """
        判断是否过期，不处理，checker使用的时候兼容系统类
        :return:
        """
        return False
