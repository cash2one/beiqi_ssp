#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-27

@author: Jay
"""
import site
import os
site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
from gevent import monkey
monkey.patch_all()
from utils.service_control.controller import MainService
from pandora import setting

class Service(MainService):
    """
    服务类
    """
    def __init__(self):
        MainService.__init__(self, setting.SERVICE_TYPE, setting.VERSION)

        from pandora.lib.service import ServicePuller
        ServicePuller().start()

    def add_cmd_opts(self, arg_parser):
        # port
        arg_parser.add_argument('--http_port', default=20000, type=int,  help="The port of the http app listen")

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    Service().start_service()
