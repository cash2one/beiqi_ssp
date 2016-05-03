#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-6

@author: Jay
"""
import ujson
from pyxmpp2.jid import JID


def xmpp_handler(xmpp_client_obj, subject):
    def xmpp_handler_fun_adaptor(handler_fun):
        xmpp_client_obj.reg_message(subject, handler_fun)
        return handler_fun
    return xmpp_handler_fun_adaptor


def xmpp_send_adaptor(use_json_dumps=True):
    """
    xmpp send 发送适配器
    :param use_json_dumps: 结果是否使用json dumps处理
    """
    def xmpp_recv_func_adaptor(fun):
        def xmpp_recv_param_adaptor(self, tgt_jid, subject, body):
            tgt_jid = tgt_jid if isinstance(tgt_jid, JID) else JID(tgt_jid)
            subject = subject.strip()
            body = ujson.dumps(body).strip() if use_json_dumps else body
            return fun(self, tgt_jid, subject, body)
        return xmpp_recv_param_adaptor
    return xmpp_recv_func_adaptor

def xmpp_recv_adaptor(use_json_loads=True):
    """
    xmpp recv 接收适配器
    :param use_json_loads: 是否使用json loads处理
    """
    def xmpp_recv_func_adaptor(fun):
        def xmpp_recv_param_adaptor(self, stanza):
            subject = stanza.subject.strip()
            body = ujson.loads(stanza.body.strip()) if use_json_loads else stanza.body
            return fun(self, stanza.from_jid, subject, body)
        return xmpp_recv_param_adaptor
    return xmpp_recv_func_adaptor