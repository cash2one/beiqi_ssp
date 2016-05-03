#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-25

@author: Jay
"""
from gevent import monkey
monkey.patch_all()

import tornado
import tornado.escape
import collections
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from utils import logger
from utils.wapper.catch import except_adaptor
from utils.service_control.setting import PT_WEB_SOCKET
from utils.network.tcp import RpcServer


class WSRpcApplication(WebSocketApplication):
    resources = {}
    handlers = {}

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def on_open(self, *args, **kwargs):
        logger.info("New WebSocket Connection was established %s" % self)
        # WSRpcApplication.waiters.add(self)


    def on_close(self, *args, **kwargs):
        logger.info('A Websocket Connection was closed %s' % self)
        # WSRpcApplication.waiters.remove(self)

    @except_adaptor()
    def on_message(self, message):
        if not message:
            logger.error("WSRpcApplication::on_message, message is None!!!")
            return

        logger.info("WSRpcApplication::on_message, message:%s, %s" % (message, self))
        message = tornado.escape.json_decode(message)
        funcName  = message.pop('funcName',None)

        if funcName not in self.handlers:
            error_msg = "WSRpcApplication::on_message, funName:%s not register, details:%s" % (funcName, self.handlers)
            logger.error(error_msg)
            return

        self.handlers[funcName](self, **message)

    @classmethod
    def reg_message(cls, subject, handler_fun):
        cls.handlers[subject] = handler_fun


class WsRpcServer(RpcServer):
    waiters = set()
    handlers = {}

    def __init__(self, ssl_args, port, application=WSRpcApplication):
        self.application = application
        patterns = {'/': application}
        res = Resource(collections.OrderedDict(sorted(patterns.items(), key=lambda t: t[0])))

        super(WsRpcServer, self).__init__(PT_WEB_SOCKET, port, WebSocketServer(('', port), res, **ssl_args))
