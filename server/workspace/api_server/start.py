#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-25

@author: Jay
"""
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
from gevent import monkey; monkey.patch_all()
import setting
from utils.service_control.controller import MainService

class Service(MainService):
    """
    服务类
    """
    def __init__(self):
        MainService.__init__(self, setting.SERVICE_TYPE,
                             setting.VERSION,
                             use_mysqldb=True,
                             db_update_dir_path=os.path.join(os.path.dirname(__file__), "db_update"))

    def add_cmd_opts(self, arg_parser):
        # db
        arg_parser.add_argument('--db_host', default=setting.DB_HOST, type=str,  help="db host")
        arg_parser.add_argument('--db_port', default=setting.DB_PORT, type=int,  help="db port")
        arg_parser.add_argument('--db_user', default=setting.DB_USER, type=str,  help="db user")
        arg_parser.add_argument('--db_password', default=setting.DB_PWD, type=str,  help="db password")
        arg_parser.add_argument('--db_name', default=setting.DB_NAME, type=str,  help="db name")

        arg_parser.add_argument('--http_port', default=8300, type=int,  help="The port of the http app listen")


if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    Service().start_service()
