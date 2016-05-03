#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-29

@author: Jay
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from utils.meta.instance_pool import InstancePool


BaseTable = declarative_base()


class OrmEngine(object):
    __metaclass__ = InstancePool

    def __init__(self, db_ip, db_port, db_name, db_user, db_pwd):
        self.register_da_rpc_client = None
        # pool_recycle 重连的时间必须小于mysql的wait_timeout，否则将被服务器拒绝，提示SQLError: (OperationalError) (2006, ‘mysql server has gone away’)
        self.mysql_db = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8' % (db_user, db_pwd, db_ip, db_port, db_name),
                                      pool_recycle=3600)
        self.SessionMaker = sessionmaker()
        self.SessionMaker.configure(bind=self.mysql_db)

    def get_session_maker(self):
        return self.SessionMaker


class OrmSession(object):
    def __init__(self, orm_engine):
        assert isinstance(orm_engine, OrmEngine)
        self.orm_engine = orm_engine

    def __enter__(self):
        assert self.orm_engine
        self.session_maker = self.orm_engine.get_session_maker()
        self.session = self.session_maker()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Must close the session
        # Fix: TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30
        # detail, see:http://stackoverflow.com/questions/3360951/sql-alchemy-connection-time-out
        self.session.close()