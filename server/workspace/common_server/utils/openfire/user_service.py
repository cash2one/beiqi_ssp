#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-10

@author: Jay
"""
import urllib
import xmltodict
from urllib2 import HTTPError
from utils import logger
from utils.network.http import HttpRpcClient
from utils.meta.singleton import Singleton
from utils.openfire.jid import JidMgr
from utils.openfire import UserAlreadyExistException
from utils.wapper.catch import except_adaptor

subscriptionType=[
    SUB_TP_SHOULD_REMOVED,          # 应该删除这个好友
    SUB_TP_NOT_ESTABLISH,           # 没有建立好友关系
    SUB_TP_HAS_SEND_REQUEST,        # 用户已经发出好友请求
    SUB_TP_RECV_REQUEST_AND_ACCEPT, # 收到好友请求并且加对方好友
    SUB_TP_FRIEND_EACH_OTHER,       # 好友已经相互添加
] = xrange(-1, 4)

class UserService(object):
    __metaclass__ = Singleton
    Authorization = "qOAWYYau"

    def __init__(self, openfire_ip=None, openfire_port=None):
        assert openfire_ip
        assert openfire_port

        self.openfire_ip = openfire_ip
        self.openfire_port = openfire_port

        self.user_http = HttpRpcClient(self.openfire_ip, self.openfire_port)

    @except_adaptor()
    def add_user(self, user_name, password):
        url = "plugins/userService/users"
        header = {"Authorization": self.Authorization,
                  "Content-Type": "application/xml"}
        body = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                  <user>
                      <username>%s</username>
                      <password>%s</password>
                  </user>""" % (user_name, password)
        return self.user_http.fetch_async(url, header, body)

    @except_adaptor()
    def del_user(self, user_name):
        url = "plugins/userService/users/%s" % user_name
        header = {"Authorization": self.Authorization}
        return self.user_http.fetch_async(url, header, method="DELETE")

    @except_adaptor()
    def new_jid(self, user_name, password):
        """
        生产jid
        :param user_name:用户名
        :param password:密码
        :return:{"jid": new_jid, "password": password}
        """
        try:
            self.add_user(user_name, password)
        except HTTPError, e:
            error_reason = xmltodict.parse(e.read())
            if error_reason.get('error', {}).get('exception', None) == UserAlreadyExistException:
                logger.warn("RegisterHandle new_jid failed!!!, jid for user_name:%s, password:%s has exist!!" % (user_name, password))
                # 由于默认user_name就是jid的user_name,所以不能出现user_name不存在，但是jid存在的情况
                # 但是由于是测试阶段，有可能手动添加JID，所以暂时忽略这种bug
                # assert False, error_reason
        new_jid = JidMgr().gen_jid(user_name, self.openfire_ip)
        return {"jid": new_jid, "password": password}

    @except_adaptor()
    def get_roster(self, user_name):
        """
        获取好友roster
        :return:
        """
        url = "plugins/userService/users/%s/roster" % user_name
        header = {"Authorization": self.Authorization}
        result = self.user_http.fetch_async(url, header)
        return xmltodict.parse(result)

    @except_adaptor()
    def is_friend(self, user_name1, user_name2):
        """
        根据好友roster判断两个用户是否是好友
        :param user_name1:
        :param user_name2:
        :return:
        """
        user1_roster = self.get_roster(user_name1).get('roster',{})
        if not user1_roster:
            return False

        roster_items = user1_roster.get("rosterItem", {})

        # rosterItem:1个元素的时候是OrderedDict;多个元素的时候是list
        if not isinstance(roster_items, list):
            roster_items = [roster_items]

        is_friend = False
        for roster_item in roster_items:
            if int(roster_item['subscriptionType']) != SUB_TP_FRIEND_EACH_OTHER:
                continue
            if JidMgr().gen_user_name(roster_item['jid']) == user_name2:
                is_friend = True
                break

        return is_friend

    @except_adaptor()
    def add_roster(self, user_name1, user_name2):
        """
        将user_name2加入到user_name1的roster好友列表里面
        注意仅仅单方面添加好友
        :param user_name1: 用户1
        :param user_name2: 用户2
        :return:
        """
        url = "plugins/userService/users/%s/roster" % user_name1
        header = {"Authorization": self.Authorization,
                  "Content-Type": "application/xml"}
        body = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                    <rosterItem>
                        <jid>%s</jid>
                        <nickname>%s</nickname>
                        <subscriptionType>3</subscriptionType>
                    <groups>
                        <group>Friends</group>
                    </groups>
                    </rosterItem>"""\
               %(JidMgr().gen_jid(user_name2, self.openfire_ip),
                 user_name2)
        return self.user_http.fetch_async(url, header, body)

    @except_adaptor()
    def add_roster_by_jid(self, jid1, jid2):
        """
        将jid2加入到jid1的roster好友列表里面
        注意仅仅单方面添加好友
        :param jid1: JID1
        :param jid2: JID2
        :return:
        """
        url = "plugins/userService/users/%s/roster" % JidMgr().gen_user_name(jid1)
        header = {"Authorization": self.Authorization,
                  "Content-Type": "application/xml"}
        body = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                    <rosterItem>
                        <jid>%s</jid>
                        <nickname>%s</nickname>
                        <subscriptionType>3</subscriptionType>
                    <groups>
                        <group>Friends</group>
                    </groups>
                    </rosterItem>"""\
               %(jid2,
                 JidMgr().gen_user_name(jid2))
        return self.user_http.fetch_async(url, header, body)

    @except_adaptor()
    def del_roster(self, user_name, del_jid):
        """
        将del_jid从user_name的roster好友列表里面移除,
        注意仅仅单方面删除好友
        :param user_name: 用户
        :param del_jid: 删除的jid
        :return:
        """
        del_jid_str = JidMgr().get_jid_str(del_jid)
        del_jid_str = urllib.quote(del_jid_str)
        url = "plugins/userService/users/%s/roster/%s" % (user_name, del_jid_str)
        header = {"Authorization": self.Authorization}
        return self.user_http.fetch_async(url, header, method="DELETE")



