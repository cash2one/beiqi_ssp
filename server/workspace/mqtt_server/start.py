#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-27

@author: Jay
"""
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
from gevent import monkey; monkey.patch_all()
from utils.service_control.controller import MainService
import setting


class Service(MainService):
    """
    服务类
    """
    def __init__(self):
        MainService.__init__(self, setting.SERVICE_TYPE, setting.VERSION)

    def init(self, args):
        """
        初始化接口
        :param args: 参数变量
        :return:
        """
        # init xmpp client
        from mqtt_server.apps.mqtt_app import MQTT_APP
        print args
        MQTT_APP().init(args.mqtt_ip, args.mqtt_port)

    def services(self, args, thread_ls):
        """
        添加服务接口
        :param args: 参数变量
        :param thread_ls: 现有的服务列表
        :return:
        """
        from mqtt_server.apps.mqtt_app import MQTT_APP
        thread_ls.append(MQTT_APP())

    def add_cmd_opts(self, arg_parser):
        """
        在获取sm参数之前，提供添加arg_parser参数接口
        :param arg_parser: 参数变量
        :return:
        """
        arg_parser.add_argument('--mqtt_ip', type=str, default=setting.MQTT_IP,  help="The ip of the mqtt server")
        arg_parser.add_argument('--mqtt_port', type=int, default=setting.MQTT_PORT, help="The port of the mqtt server")

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    Service().start_service()
