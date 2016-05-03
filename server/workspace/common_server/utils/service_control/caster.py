#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-3

@author: Jay
"""
import sys
import ujson
from utils.network.udp import UdpClient
from utils.scheduler import Jobs
from utils import logger
from utils.service_control.finder import get_cur_ip
from cacher import ParamCacher
from setting import SM_UDP_PORT


BEAT_INTERVAL = 4
TIMEOUT = 15
TIMEOUT_INTERVAL = TIMEOUT+1

class HeartBeatClient(UdpClient):
    def __init__(self, ip, port, msg):
        self.msg = msg
        super(HeartBeatClient, self).__init__(ip, port)

    def advertise(self):
        return Jobs().add_interval_job(BEAT_INTERVAL, self.beat)

    def beat(self):
        try:
            send_msg = self.msg if not callable(self.msg) else self.msg()
            self.send_async(send_msg)
        except Exception, e:
            if 'Operation not permitted' not in str(e):     # we firewall ourselves sometimes to isolate servers
                logger.error('Error while heartbeating: %s', e)


class ServiceAdvertiser(HeartBeatClient):
    def __init__(self, service_group, port, jid, service_version,  servie_mgr_ip=None, servie_mgr_port=None, default_load=1, load_getter=None):
        self.service_group = service_group
        self.port = port
        self.jid = jid
        self.service_version = service_version
        self.default_load = default_load
        self.current_load = default_load
        self.load_getter = load_getter
        self.process_name = sys.argv[0]
        self.running = False

        if not servie_mgr_ip:
            servie_mgr_ip = ParamCacher().sm_ip
        if not servie_mgr_port:
            servie_mgr_port = SM_UDP_PORT

        super(ServiceAdvertiser,self).__init__(servie_mgr_ip, servie_mgr_port, self.get_msg)

    def advertise(self):
        self.running = True
        return super(ServiceAdvertiser,self).advertise()

    def update_load(self, load):
        self.current_load = load

    def get_msg(self):
        if self.load_getter:
            self.update_load(self.load_getter() or self.default_load)

        running = self.running
        return ujson.dumps([self.service_group,
                            get_cur_ip(),
                            self.port,
                            self.jid,
                            self.service_version,
                            self.current_load,
                            running])

    def notify_shutdown(self):
        self.running = False
        self.beat()