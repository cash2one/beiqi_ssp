# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from utils.network.tcp import TcpRpcServer
from utils.meta.singleton import Singleton


class TcpRpcApp(TcpRpcServer):
    __metaclass__ = Singleton

    def __init__(self, port):
        from service_mgr.logic.rpc.handler import TcpHandler
        super(TcpRpcApp, self).__init__(port, TcpHandler)
