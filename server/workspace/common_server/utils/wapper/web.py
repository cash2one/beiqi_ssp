#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-28

@author: Jay
"""
import sys
import traceback
import ujson
from utils import logger
from utils.comm_func import strip_dic_list
from utils.service_control.parser import ArgumentParser
from utils.wapper.stackless import gevent_adaptor


def enc_utf8(v):
    return v.encode('utf-8') if isinstance(v, unicode) else v


def web_adaptor(use_json_dumps=True, use_http_render=True, http_sign=None, body_parser_fun=None):
    """
    客户端请求的网络适配器，
    :param use_json_dumps: 结果是否使用json dumps处理
    :param use_http_render: 是否使用http渲染引擎
    :param http_sign: http签名
    """
    def need_json_dumps():
        return use_json_dumps

    def param_process(self, args, kwargs):
        kwargs.update(dict((enc_utf8(k.strip()), enc_utf8(value[-1].strip())) for k, value in self.request.arguments.items()))

        if body_parser_fun:
            body_parser_fun(args, kwargs, self.request.body)

        # 暂时不控制，允许所有跨域访问
        self.set_header('Access-Control-Allow-Origin','*')

    def before_access_process(self, args, kwargs):
        http_req_log = "receive http request:" + '\n'
        http_req_log += "protocol:" + self.request.protocol + '\n'
        http_req_log += "method:" + self.request.method + '\n'
        http_req_log += "uri:" + self.request.uri + '\n'
        http_req_log += "headers:" + str(self.request.headers) + '\n'
        http_req_log += "body_arguments:" + ujson.dumps(self.request.body_arguments) + '\n'
        http_req_log += "body:" + self.request.body + '\n'
        if self.request.path != "/ping":
            logger.info(http_req_log)

        param_process(self, args, kwargs)

    def after_access_process(self, args, kwargs):
        if http_sign and ArgumentParser().args.use_sign:
            self.result['sign'] = http_sign

        if not use_http_render:
            return

        if self.result is None:
            return

        if need_json_dumps():
            self.write(ujson.dumps(self.result))
        else:
            self.write(self.result)

    def except_process(self, args, kwargs):
        exec_info = sys.exc_info()
        tracl_back_data = "Please check its parameters or may be server meet some issue!!!!!!!!!!!!!\n"
        tracl_back_data += "req ip:%s"%(str(self.request.remote_ip)) + '\n'
        tracl_back_data += "req url:%s"%(str(self.request.path)) + '\n'
        tracl_back_data += "req headers:%s"%(str(self.request.headers)) + '\n'
        tracl_back_data += "req params:%s"%(str(args)) + '\n'
        tracl_back_data += "req kwargs:%s"%(str(kwargs)) + '\n'
        tracl_back_data += "req request.arguments:%s"%(str(self.request.arguments)) + '\n'
        tracl_back_data += str(exec_info[0]) + ":" + str(exec_info[1]) + '\n'
        tracl_back_data += traceback.format_exc()

        logger.error(tracl_back_data)
        self.set_status(400)
        self.write(tracl_back_data)

    def finally_process(self, args, kwargs):
        """
        Flushes the current output buffer to the network.
        """
        if not use_http_render:
            return

        if self.result:
            self.flush()
            # STOP asynchronous wait
            self.finish()

    def web_func_adaptor(fun):
        @gevent_adaptor(True)
        def web_param_adaptor(self, *args, **kwargs):
            try:
                before_access_process(self, args, kwargs)
                self.result = fun(self, *args, **kwargs)
                after_access_process(self, args, kwargs)
            except:
                except_process(self, args, kwargs)
            finally:
                finally_process(self, args, kwargs)
        return web_param_adaptor
    return web_func_adaptor

AJAX_DATA_LS_KEY = "js_data"
def ajax_recv_wapper():
    def ajax_recv_func_wapper(fun):
        def ajax_recv_param_wapper(self, *args, **kwargs):
            ajax_data_ls = ujson.loads(kwargs.pop(AJAX_DATA_LS_KEY, "[]"))
            strip_dic_list(ajax_data_ls)
            kwargs[AJAX_DATA_LS_KEY] = ajax_data_ls
            return fun(self, *args, **kwargs)
        return ajax_recv_param_wapper
    return ajax_recv_func_wapper
