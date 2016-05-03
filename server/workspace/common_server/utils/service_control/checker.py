#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-5

@author: Jay
"""
import time
import os
from gsocketpool import Pool
from gsocketpool import TcpConnection
from utils.scheduler import Jobs
from utils import logger
from utils.network.tcp import TcpRpcClient
from utils.network.http import HttpRpcClient
from utils.network import PING_RESPONSE
from utils.wapper.stackless import gevent_adaptor
from utils.data.db import orm

class Checker(object):
    def __init__(self, ip, port):
        self.ip = ip
        self._port = port
        self._pool = self._init_pool()

    def _init_pool(self):
        pass

    @gevent_adaptor()
    def ping(self):
        pass

    @property
    def port(self):
        return self._port

    def __str__(self):
        return "%s:%s:%s" % (self.__class__.__name__, self.ip, self._port)


class MysqlChecker(Checker):
    def __init__(self, db_host, db_port, db_name, db_user, db_password):
        self._db_port = db_port
        self.orm_engine = orm.OrmEngine(db_host, db_port, db_name, db_user, db_password)

    @gevent_adaptor()
    def ping(self):
        try:
            with orm.OrmSession(self.orm_engine) as session:
                session.execute("SELECT 1")
                result = PING_RESPONSE
        except:
            result = ""
        return result

    @property
    def port(self):
        return self._db_port


class TcpCommonChecker(Checker):
    def _init_pool(self):
        return Pool(TcpConnection, dict(host=self.ip, port=self._port))

    @gevent_adaptor()
    def ping(self):
        with self._pool.connection() as conn:
            if conn.is_connected():
                return PING_RESPONSE


class TcpCustomChecker(TcpCommonChecker):
    def _init_pool(self):
        return Pool(TcpRpcClient, dict(host=self.ip, port=self._port))

    @gevent_adaptor()
    def ping(self):
        with self._pool.connection() as conn:
            return conn.ping()


class HttpCustomChecker(TcpCustomChecker):
    def _init_pool(self):
        return Pool(HttpRpcClient, dict(host=self.ip, port=self._port))


class HttpsCustomChecker(TcpCustomChecker):
    def _init_pool(self):
        return Pool(HttpRpcClient, dict(host=self.ip, port=self._port, ssl=True))


# SECOND
HEARTBEAT_EXPIRE_TIME = 30
TIMEOUT_INTERVAL = 16
TIMEOUT_GRACE = 60
class PortChecker(object):
    def __init__(self, port_info, ip="localhost", check_interval=TIMEOUT_INTERVAL):
        """
        :param port_ino: 支持以下两个数据格式
         1.   [{"type":"http/https/tcp/...", "port":"1111"}]
         2.   {"http/https/tcp/...":1111,,,,,}
        :param ip:
        :param check_interval:
        :return:
        """
        self.ip = str(ip)
        self.port_ls = port_info if isinstance(port_info, list) else [{"type": k, "port": v} for k, v in port_info.items()]
        self.check_interval = check_interval
        self.checks = []
        self.timing_out = False
        self.last_connect_dic = {}
        self.init_checks()
        self.job = None

    def _get_checker(self, type, port):
        if type == "tcp":
            return TcpCommonChecker(self.ip, port)
        elif type == "http":
            return HttpCustomChecker(self.ip, port)
        elif type == "https":
            return HttpsCustomChecker(self.ip, port)
        return None

    def init_checks(self):
        for port_dic in self.port_ls:
            checker = self._get_checker(port_dic['type'], port_dic['port'])
            if not checker:
                logger.warn("PortChecker::init_checks protocol:%s, port:%s not checker!!!" % (port_dic['type'], port_dic['port']))
                continue
            self.checks.append(checker)

            self.last_connect_dic.setdefault(checker.port, time.time())

    def is_timeing_out(self):
        return self.timing_out

    def start(self):
        self.job = Jobs().add_interval_job(self.check_interval, self.check)

    def stop(self):
        self.job.stop()

    def _on_disconnected(self, checker, since_connected):
        logger.error('Unable to connect to my port:%s for %s: killing myself' % (checker.port, since_connected))
        os.kill(os.getpid(), 9)

    def _on_connected(self):
        pass

    def __on_ping_success(self, checker):
        self.last_connect_dic[checker.port] = time.time()
        self.timing_out = False
        self._on_connected()

    def __on_ping_timeout(self, checker):
        self.timing_out = True

        since_connected = int(time.time() - self.last_connect_dic[checker.port])

        if since_connected > 2*TIMEOUT_GRACE:
            logger.error('Unable to connect to my port:%s for %s' % (checker.port, since_connected))
            self._on_disconnected(checker, since_connected)
        elif since_connected > TIMEOUT_GRACE:
            logger.error('Unable to connect to my port:%s for %s' % (checker.port, since_connected))
        else:
            logger.warn('Unable to connect to my port:%s. Checking again later'% checker.port )

    def check(self):
        for checker in self.checks:
            try:
                assert checker.ping() == PING_RESPONSE
            except:
                self.__on_ping_timeout(checker)
                continue

            self.__on_ping_success(checker)
