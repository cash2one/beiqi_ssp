#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-10

@author: Jay
"""
from utils.regex import IP_REGEX
from pyxmpp2.jid import JID

class JidMgr(object):

    @staticmethod
    def gen_jid(user_name, openfire_ip):
        """
        由用户名获取jid字符串
        :param user_name:用户名
        :param openfire_ip:openfire ip
        :return:
        """
        return '%s@%s' % (user_name, openfire_ip)

    @staticmethod
    def is_jid(jid):
        """
        判断是否是JID
        :param jid: 字符串
        :return:True or False
        """
        user_name, openfire_ip = jid.split("@")
        return IP_REGEX.search(openfire_ip) if user_name else False

    @staticmethod
    def gen_user_name(jid):
        """
        由JID获取用户名
        :param jid:
        :return:
        """
        return jid.local if isinstance(jid, JID) else jid.split("@")[0]

    @staticmethod
    def get_jid_str(jid):
        """
        获取jid字符串：aaa@bbb/xxx形式
        :param jid:
        :return:
        """
        return str(jid.as_string()) if isinstance(jid, JID) else str(jid)

    @staticmethod
    def get_jid_bare_str(jid):
        """
        获取裸的jid字符串：aaa@bbb形式
        :param jid:
        :return:
        """
        return jid.bare().as_string() if isinstance(jid, JID) else jid
