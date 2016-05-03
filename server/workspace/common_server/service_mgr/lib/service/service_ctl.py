#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016-3-23

@author: Jay
"""
from service_mgr.logic.rpc.sender.cs_to_gs import GsRpcClient
from service_mgr.lib.service import IServiceCompose


class ServiceCtl(IServiceCompose):
    def __init__(self, service_obj):
        self.__service_obj = service_obj
        self._control_rpc = None

    @staticmethod
    def name():
        return "sctl"

    def start(self):
        self._prepare()

    def _prepare(self):
        if self._control_rpc:
            return

        tcp_port = self.__service_obj.port.get('tcp', None)
        assert tcp_port
        self._control_rpc = GsRpcClient(self.__service_obj.ip, tcp_port)
        assert self._control_rpc

    @property
    def control_rpc(self):
        self._prepare()
        return self._control_rpc
