#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-4

@author: Jay
"""
import signal
import platform
import gevent
from utils.meta.singleton import Singleton
from utils import logger


class ExitHandler(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.exit_handlers = []

        gevent.signal(signal.SIGINT, lambda *args: self._exit(*args))
        gevent.signal(signal.SIGTERM, lambda *args: self._exit(*args))
        if platform.system() == 'Linux':
            gevent.signal(signal.SIGQUIT, lambda *args: self._exit(*args))

    def add_exit_handler(self, handler):
        self.exit_handlers.append(handler)

    def _exit(self, *args):
        logger.warn("ExitHandler::_exit success!!, args:%s" % str(args))

        for handler in self.exit_handlers:
            handler()
