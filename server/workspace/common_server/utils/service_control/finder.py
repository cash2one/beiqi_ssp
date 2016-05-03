#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-8

@author: Jay
"""
import re
import urllib2
import platform
from subprocess import Popen, PIPE
from gevent import socket
from utils.meta.singleton import Singleton


class IpFinder(object):
    __metaclass__ = Singleton

    is_extranet = False

    def __init__(self):
        self.ip_dic = {}

    @staticmethod
    def get_outer_net_ip():
        url_ls = ["http://www.whereismyip.com", "http://www.ip138.com/ip2city.asp", "http://ml"]
        for url in url_ls:
            try:
                ip = re.search('\d+\.\d+\.\d+\.\d+', urllib2.urlopen(url).read()).group(0)
                return ip
            except:
                pass
        assert False, "Not found outer net ip!!!!"

    def get_cache_outer_net_ip(self):
        outer_ip = self.ip_dic.get("outer_ip", None)
        if not outer_ip:
            outer_ip = self.get_outer_net_ip()
            self.ip_dic["outer_ip"] = outer_ip
        return outer_ip

    @staticmethod
    def get_inter_net_ip():
        if platform.system() == 'Linux':
            cmd = "ifconfig"
        else:
            cmd = "ipconfig"
        return re.search('\d+\.\d+\.\d+\.\d+', Popen(cmd, stdout=PIPE).stdout.read()).group(0)

    def get_cache_inter_net_ip(self):
        inter_ip = self.ip_dic.get("inter_ip", None)
        if not inter_ip:
            inter_ip = self.get_inter_net_ip()
            self.ip_dic["inter_ip"] = inter_ip
        return inter_ip


def get_cur_ip():
    if IpFinder().is_extranet:
        return IpFinder().get_cache_outer_net_ip()
    else:
        return IpFinder().get_cache_inter_net_ip()


def get_random_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
