#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
import site
import os
site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
from gevent import monkey
monkey.patch_all()

import time
from service_mgr import setting
from utils.service_control.controller import MainService
from utils.service_control.parser import parser_boolean


class Service(MainService):
    def __init__(self):
        super(Service, self).__init__(setting.SERVICE_TYPE,
                                      setting.VERSION,
                                      is_sm=True,
                                      db_update_dir_path=os.path.join(os.path.dirname(__file__), "db_update"),
                                      use_mysqldb=True)

    def init(self, args):
        from service_mgr.logic.logic_mgr import LogicMgr
        LogicMgr().init()

    def exit(self):
        super(Service, self).exit()
        self.update()

    def update(self):
        super(Service, self).update()
        cur_time = time.time()
        from service_mgr.logic.logic_mgr import LogicMgr
        LogicMgr().update(cur_time)

    def services(self, args, thread_ls):
        from service_mgr.apps.rpc_app import TcpRpcApp
        from service_mgr.apps.udp_app import HeartbeatApp

        thread_ls.append(TcpRpcApp(args.tcp_port))
        thread_ls.append(HeartbeatApp(args.udp_port))

    def add_cmd_opts(self, arg_parser):
        # port
        from utils.service_control.setting import SM_TCP_PORT, SM_HTTP_PORT, SM_UDP_PORT
        arg_parser.add_argument('--is_https', default=False, type=parser_boolean,  help="Is use http ssl connection")
        arg_parser.add_argument('--http_port', default=SM_HTTP_PORT, type=int,  help="The port of the http app listen")
        arg_parser.add_argument('--tcp_port', default=SM_TCP_PORT, type=int,  help="The port of the tcp rpc app listen")
        arg_parser.add_argument('--udp_port', default=SM_UDP_PORT, type=int,  help="The port of the udp app listen")

        # db
        arg_parser.add_argument('--db_host', default=setting.DB_HOST, type=str,  help="db host")
        arg_parser.add_argument('--db_port', default=setting.DB_PORT, type=int,  help="db port")
        arg_parser.add_argument('--db_user', default=setting.DB_USER, type=str,  help="db user")
        arg_parser.add_argument('--db_password', default=setting.DB_PWD, type=str,  help="db password")
        arg_parser.add_argument('--db_name', default=setting.DB_NAME, type=str,  help="db name")
        
if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    Service().start_service()
