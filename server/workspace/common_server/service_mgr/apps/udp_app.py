#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-3

@author: Jay
"""
from utils.network.udp import UdpServer
from utils.wapper.stackless import gevent_adaptor
import ujson
from service_mgr.lib.service.service_main import ServiceMgr, Service
from service_mgr.lib.service_group import ServiceGrpMgr
from service_mgr.lib.service.service_hb import ServiceHeartBeat


class HeartbeatApp(UdpServer):
    def __init__(self, port):
        super(HeartbeatApp, self).__init__(port)

    @gevent_adaptor()
    def handle(self, data, address):
        service_group, ip, port, jid, service_version, current_load, stat = ujson.loads(data)

        ServiceGrpMgr().add_grp_id(service_group)

        service_id = Service.make_id(service_group, ip, port)
        service_obj = ServiceMgr().get_service_by_id(service_id)
        if not service_obj:
            service_obj = ServiceMgr().new_service(service_group, ip, port, jid)

        service_obj.find_cp(ServiceHeartBeat.name()).heart_beat(service_version, current_load, stat)
