#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-8

@author: Jay
"""
import ujson


def tcp_send_adaptor(use_json_dumps=True):
    """
    :param use_json_dumps: 结果是否使用json dumps处理
    """
    def need_json_dumps():
        return use_json_dumps

    def after_access_process(self, args, kwargs):
        if need_json_dumps():
            self.result = ujson.dumps(self.result)

    def tcp_send_func_adaptor(fun):
        def tcp_send_param_adaptor(self, *args, **kwargs):
            self.result = fun(self, *args, **kwargs)
            after_access_process(self, args, kwargs)
            return self.result
        return tcp_send_param_adaptor
    return tcp_send_func_adaptor


def tcp_recv_adaptor(use_json_loads=True):
    """
    tcp rpc 接收适配器
    :param use_json_loads: 是否使用json loads处理
    """
    def tcp_recv_func_adaptor(fun):
        def tcp_recv_param_adaptor(self, *args, **kwargs):
            args = ujson.loads(args[0]) if use_json_loads else args
            for k, v in args.items():
                kwargs[k.strip()] = v.strip() if isinstance(v, str) or isinstance(v, unicode) else v
            return fun(self, **kwargs)
        return tcp_recv_param_adaptor
    return tcp_recv_func_adaptor
