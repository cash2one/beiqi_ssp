#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016-3-22

@author: Jay
"""
import platform
from utils.scheduler import Jobs
from utils.data.db import mysql_util
from utils import logger
from service_mgr.lib.service import IServiceCompose
from service_ctl import ServiceCtl


MYSQL_DB_BACKUP_HOUR = 2
class ServiceBackup(IServiceCompose):
    def __init__(self, service_obj):
        self.__service_obj = service_obj
        self.db_params = None
        self.job = None

    @staticmethod
    def name():
        return "sbp"

    def start(self):
        self.job = Jobs().add_cron_job(self.__backup, hour=MYSQL_DB_BACKUP_HOUR)

    def stop(self):
        Jobs().remove_job(self.job)

    def _prepare(self):
        if self.db_params:
            return

        self.db_params = self.__service_obj.find_cp(ServiceCtl.name()).control_rpc.get_db_params()
        assert self.db_params

    def __backup(self):
        self._prepare()

        mysql_util.MysqlUtil.db_dump(self.db_params["db_host"],
                                     self.db_params["db_port"],
                                     self.db_params["db_user"],
                                     self.db_params["db_password"],
                                     self.db_params["db_name"],
                                     use_gzip=True if platform.system() == 'Linux' else False)
        logger.info("Service::__backup success!!! db_params:%s" % self.db_params)