#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-30

@author: Jay
"""
from utils.data.db import orm


def orm_adaptor(orm_engin):
    def orm_fun_adaptor(fun):
        def orm_param_adptor(self, *args, **kwargs):
            with orm.OrmSession(orm_engin) as session:
                try:
                    kwargs['orm_session'] = session
                    result = fun(self, *args, **kwargs)
                    session.flush()
                    session.commit()
                except Exception, _:
                    session.rollback()
                    raise
                return result
        return orm_param_adptor
    return orm_fun_adaptor