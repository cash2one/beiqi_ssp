#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from gevent import monkey
monkey.patch_all()
import gevent
from pyxmpp2.jid import JID
from pyxmpp2.client import Client
from pyxmpp2.settings import XMPPSettings
from pyxmpp2.interfaces import XMPPFeatureHandler
from pyxmpp2.streamevents import ConnectingEvent, DisconnectedEvent
from pyxmpp2.roster import RosterReceivedEvent, RosterUpdatedEvent
from pyxmpp2.interfaces import message_stanza_handler, presence_stanza_handler, QUIT
from pyxmpp2.interfaces import EventHandler, event_handler
from pyxmpp2.streamevents import AuthorizedEvent
from pyxmpp2.presence import Presence
from pyxmpp2.message import Message
from utils import logger
from utils.wapper.catch import except_adaptor
from utils.service_control.setting import PT_XMPP
from utils.openfire.user_service import UserService
from utils.openfire.jid import JidMgr
from utils.wapper.stackless import gevent_adaptor
from utils.wapper.xmpp import xmpp_recv_adaptor, xmpp_send_adaptor


def roster_item_2_dic(roster_item):
    """
    xmpp roster item 转成dic
    :param roster_item:
    :return:
    """
    if not roster_item:
        return {}
    return {"jid": roster_item.jid.bare().as_string(),
            "name": roster_item.name,
            "groups": roster_item.groups,
            "subscription": roster_item.subscription}

class XMPPClient(EventHandler, XMPPFeatureHandler):
    """
    xmpp 客户端
    """
    def __init__(self):
        self.subject_to_fun_dic = {}
        self.xmpp_client = None
        self.is_auth = False
        self.protocol = PT_XMPP
        self.jid_bare_str = None

    def init(self, jid, password, c2s_port=5222):
        """
        初始化
        :param jid: jid
        :param password: 密码
        :return:
        """
        self.JID = jid if isinstance(jid, JID) else JID(jid)
        self.jid_bare_str = self.JID.bare().as_string()
        self.password = password
        self.settings = XMPPSettings({u"password": password,
                                      u"starttls": True,
                                      u"tls_verify_peer": False,
                                      u"c2s_port":c2s_port})
        if c2s_port != 5222:
            logger.warn("XMPPClient::init c2s_port is :%s!!!!!" % c2s_port)

    @gevent_adaptor(use_join_result=False)
    def start(self):
        """
        服务开始
        :return:
        """
        logger.warn("XMPPClient::start listen on %s:%s:%s" % (self.protocol, self.JID, self.password))
        self.xmpp_client = Client(self.JID, [self], self.settings)
        self.xmpp_client.connect()
        self.xmpp_client.run()
        self.is_auth = False

    def stop(self):
        """
        Request disconnection and let the main loop run for a 2 more
        seconds for graceful disconnection.
        """
        logger.warn("XMPPClient::stop listen on %s:%s:%s" % (self.protocol, self.JID, self.password))
        assert self.xmpp_client
        self.xmpp_client.disconnect()
        self.xmpp_client.run(timeout=2)
        self.is_auth = False

    def restart(self):
        """
        服务重启
        :return:
        """
        logger.warn("XMPPClient::restart listen on %s:%s:%s" % (self.protocol, self.JID, self.password))
        self.stop()
        self.start()

    @xmpp_send_adaptor()
    def _send(self, tgt_jid, subject, body):
        """
        发送消息
        :param tgt_jid:目的jid
        :param subject: 主题
        :param body:  文本
        :return:
        """
        if not self.xmpp_client.stream:
            self.restart()
        self.wait_for_auth()

        tgt_jid = tgt_jid if isinstance(tgt_jid, JID) else JID(tgt_jid)
        msg = Message(to_jid=tgt_jid, body=body, subject=subject,stanza_type="normal")

        # _send与send的区别，send的锁有点奇怪，有时候会卡主,暂时不用锁
        # def send(self, stanza):
        # """Write stanza to the stream.
        #
        # :Parameters:
        #     - `stanza`: XMPP stanza to send.
        # :Types:
        #     - `stanza`: `pyxmpp2.stanza.Stanza`
        # """
        # with self.lock:
        #     return self._send(stanza)
        self.xmpp_client.stream._send(msg)
        logger.info("XMPPClient::_send, src_jid:%s ,src_pass:%s, des_jid:%s, subject:%s, body:%s" %\
                    (self.JID,self.password, tgt_jid, subject, body))

    @gevent_adaptor()
    def send_async(self, sto_jid, ssubject, sbody):
        """
        协程非阻塞发送
        :param sto_jid:
        :param ssubject:
        :param sbody:
        :return:
        """
        self._send(sto_jid, ssubject, sbody)

    def send_sync(self, sto_jid, ssubject, sbody):
        """
        阻塞发送
        :param sto_jid:
        :param ssubject:
        :param sbody:
        :return:
        """
        self._send(sto_jid, ssubject, sbody)

    @event_handler(ConnectingEvent)
    def handle_connected(self, event):
        """
        XMPP 连接成功
        :param event:
        :return:
        """
        pass

    @event_handler(DisconnectedEvent)
    def handle_disconnected(self, event):
        """
        XMPP 断开连接
        :param event:
        :return:
        """
        """Quit the main loop upon disconnection."""
        logger.error("XMPPClient::handle_disconnected: JID:%s!!! event:%s" % (self.JID, event))
        return QUIT

    @event_handler(AuthorizedEvent)
    def handle_authorized(self, event):
        """
        OPENFIRE 授权成功
        :param event:
        :return:
        """
        logger.info("XMPPClient::handle_authorized: JID:%s!!!" % self.JID)
        self.is_auth = True

    @event_handler(RosterReceivedEvent)
    def handle_roster_received(self, event):
        """
        XMPP 接收到roster列表
        :param event:
        :return:
        """
        return True

    @event_handler(RosterUpdatedEvent)
    def handle_roster_update(self, event):
        """
        XMPP 接收到roster列表更新
        :param event:
        :return:
        """
        log_params = "jid:%s item:%s old_item:%s" % (self.jid_bare_str,
                                                     roster_item_2_dic(event.item),
                                                     roster_item_2_dic(event.old_item))
        logger.info("XMPPClient::handle_roster_update, %s" % log_params)

        added_ls = []
        removed_ls = []
        modified_ls = []

        item = event.item
        if item.subscription == "remove":
            self.on_roster_del_notify(item)
            removed_ls.append(item)
        elif item.subscription == "both":
            self.on_roster_add_notify(item)
            modified_ls.append(item) if event.old_item else added_ls.append(item)

        self.on_roster_update_notify(added_ls, removed_ls, modified_ls)

    def reg_message(self, subject, hander_fun):
        """
        注册主题接收回调
        :param subject: 主题
        :param hander_fun: 回调函数
        :return:
        """
        self.subject_to_fun_dic[subject] = hander_fun

    @message_stanza_handler("normal")
    @except_adaptor()
    @xmpp_recv_adaptor()
    def handle_message(self, from_jid, subject, body):
        """
        消息接收分发
        :param from_jid: 发送者jid
        :param subject: 发送主题
        :param body: 发送内容
        :return:
        """
        if subject not in self.subject_to_fun_dic:
            error_msg = "subject:%s not register, details:%s" % (subject, self.subject_to_fun_dic)
            logger.error(error_msg)
            return True

        self.subject_to_fun_dic[subject](self, from_jid, body)
        return True

    @presence_stanza_handler()
    @except_adaptor()
    def handle_presence_available(self, stanza):
        """
        XMPP 上线通知
        :param stanza:
        :return:
        """
        return True

    @presence_stanza_handler("unavailable")
    @except_adaptor()
    def handle_presence_unavailable(self, stanza):
        """
        XMPP 下线通知
        :param stanza:
        :return:
        """
        return True

    @presence_stanza_handler("subscribe")
    def handle_presence_subscribe(self, stanza):
        """
        上下线状态预定请求
        :param stanza:
        :return:
        """
        presence = Presence(to_jid=stanza.from_jid.bare(), stanza_type="subscribe")
        return [stanza.make_accept_response(), presence]

    @presence_stanza_handler("subscribed")
    def handle_presence_subscribed(self, stanza):
        """
        上下线状态预定通知
        :param stanza:
        :return:
        """
        return True

    @presence_stanza_handler("unsubscribe")
    def handle_presence_unsubscribe(self, stanza):
        """
        上下线状态取消预定请求
        :param stanza:
        :return:
        """
        if not self.is_jid_in_roster(stanza.from_jid):
            return True
        presence = Presence(to_jid=stanza.from_jid.bare(), stanza_type="unsubscribe")
        return [stanza.make_accept_response(), presence]

    @presence_stanza_handler("unsubscribed")
    def handle_presence_unsubscribed(self, stanza):
        """
        上下线状态取消预定通知
        :param stanza:
        :return:
        """
        return True

    def is_jid_in_roster(self, jid):
        """
        判断某个jid是否在roster中
        :param jid: jid
        :return:True/False
        """
        if not self.xmpp_client.roster_client.roster:
            return False

        for item in self.xmpp_client.roster_client.roster.items():
            if JidMgr().get_jid_str(item.jid) == JidMgr().get_jid_str(jid):
                return True
        return False

    @gevent_adaptor(use_join_result=False)
    def add_roster(self, Jid, name=None, groups=None):
        """
        添加好友
        :param Jid: 添加的jid
        :param name: 添加的用户名
        :param groups: 添加的用户组
        :return:
        """
        if self.is_jid_in_roster(Jid):
            return

        self.xmpp_client.roster_client.add_item(Jid, name, groups)
        self.xmpp_client.stream._send(Presence(to_jid=Jid, stanza_type='subscribe'))
        # 注意：以下方式也可以实现添加roster功能，但是用userservice 的add roster则没有handle_presence_available通知
        # UserService().add_roster(self.JID.local, Jid.local)
        # UserService().add_roster(Jid.local, self.JID.local)

    @gevent_adaptor(use_join_result=False)
    def del_roster(self, Jid):
        """
        删除好友
        :param Jid: 删除的jid
        :return:
        """
        if isinstance(Jid, str) or isinstance(Jid, unicode):
            Jid = JID(Jid)

        if not self.is_jid_in_roster(Jid):
            return
        UserService().del_roster(self.JID.local, Jid.bare().as_string())
        UserService().del_roster(Jid.local, self.JID.as_string())
        self.xmpp_client.stream._send(Presence(to_jid=Jid, stanza_type='unsubscribe'))

    def on_roster_del_notify(self, roster_item):
        """
        roster删除成功通知
        :param roster_item: RosterItem 对象
        :return:
        """
        pass

    def on_roster_add_notify(self, roster_item):
        """
        roster添加成功通知
        :param roster_item: RosterItem 对象
        :return:
        """
        pass

    def on_roster_update_notify(self, added_ls, removed_ls, modified_ls):
        """
        roster添加成功通知
        :param added_ls: added_ls RosterItem 列表
        :param removed_ls: removed RosterItem 列表
        :param modified_ls: modified RosterItem 列表
        :return:
        """
        pass

    def wait_for_auth(self):
        """
        等待xmpp登陆授权成功
        :return:
        """
        while not self.is_auth:
            logger.warn("XMPPClient::wait_for_auth, sleep 1s to wait for auth")
            gevent.sleep(5)
