#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-7

@author: Jay
"""
import traceback
import sys
from urllib2 import HTTPError
import sqlalchemy.exc
from utils import logger
from utils import error_code


def except_adaptor(is_raise=True, default_result=None):
    def except_fun_adaptor(fun):
        def except_param_adptor(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except:
                exec_info = sys.exc_info()
                track_back_data = "%s Error!!!!!!!!!!!!!\n" % fun.__name__
                track_back_data += "args:%s" % str(args) + '\n'
                track_back_data += "kwargs:%s" % str(kwargs) + '\n'
                track_back_data += str(exec_info[0]) + ":" + str(exec_info[1]) + '\n'
                track_back_data += traceback.format_exc()
                logger.error(track_back_data)
                if is_raise:
                    raise
            if default_result:
                return default_result
        return except_param_adptor
    return except_fun_adaptor


def http_except_adapter():
    def proxy_error_fun_adapter(fun):
        def proxy_error_param_adapter(self, *args, **kwargs):
            try:
                return fun(self, *args, **kwargs)
            except HTTPError, e:
                logger.error(traceback.format_exc())
                self.set_status(e.code)
                return e.msg
            except:
                logger.error(traceback.format_exc())
                self.set_status(400)
                return "can't process your request, pls check your service and url!!!\n%s" % traceback.format_exc()
        return proxy_error_param_adapter
    return proxy_error_fun_adapter


def orm_except_adapter():
    def orm_except_fun_adapter(fun):
        def orm_except_param_adapter(self, *args, **kwargs):
            result = {}
            exe_error = None
            exe_error_code = None
            try:
                result = fun(self, *args, **kwargs)
            except sqlalchemy.exc.SQLAlchemyError, error:
                exe_error = error
                exe_error_code = error_code.ERROR_DB_ERROR
            except Exception, error:
                exe_error = error
                exe_error_code = error_code.ERROR_UNKNOWN_ERROR
            finally:
                if exe_error:
                    logger.error("orm_except_adapter ERROR!!! fun:%s, %s" % (fun.__name__, traceback.format_exc()))
                    result['result'] = exe_error_code
            return result
        return orm_except_param_adapter
    return orm_except_fun_adapter