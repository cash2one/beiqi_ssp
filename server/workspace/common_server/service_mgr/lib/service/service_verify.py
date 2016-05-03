#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016-3-23

@author: Jay
"""
from utils import logger
from utils.scheduler import Jobs
from service_mgr.lib.service import IServiceCompose
from service_ctl import ServiceCtl

SERVICE_VERIFY_INTERVAL_SECONDS = 60
class ServiceVerify(IServiceCompose):
    def __init__(self, service_obj):
        self.__service_obj = service_obj
        self.job = None

    @staticmethod
    def name():
        return "svry"

    def start(self):
        self.job = Jobs().add_interval_job(SERVICE_VERIFY_INTERVAL_SECONDS, self.__verify)

    def stop(self):
        Jobs().remove_job(self.job)

    def _is_valid(self):
        try:
            is_valid = self.__service_obj.find_cp(ServiceCtl.name()).control_rpc.verify()
        except:
            is_valid = False
        return is_valid

    def __verify(self):
        is_valid = self._is_valid()
        if not is_valid:
            self._invalid()
            return

    def _invalid(self):
        logger.warn("ServiceVerify::_invalid!!! service:%s will stop" % self.__service_obj.id)
        self.__service_obj.stop()
