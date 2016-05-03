#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-27

@author: Jay
"""
from utils.openfire.jid import JidMgr

"""
CLIENT 2 SERVER
"""
C_PUB_XMPP_LOGIN_REQ = lambda shost, jid: "xmpp_login_req/%s/%s" % (shost, JidMgr().get_jid_str(jid))
C_PUB_XMPP_LOGOUT_REQ = lambda shost, mxid: "xmpp_logout_req/%s/%s" % (shost, mxid)
C_PUB_XMPP_ROSTER_ADD_REQ = lambda shost, mxid: "xmpp_roster_add_req/%s/%s" % (shost, mxid)
C_PUB_XMPP_ROSTER_DEL_REQ = lambda shost, mxid: "xmpp_roster_del_req/%s/%s" % (shost, mxid)
C_PUB_XMPP_MESSAGE_SEND = lambda shost, mxid: "xmpp_message_send/%s/%s" % (shost, mxid)
C_PUB_XMPP_MESSAGE_BCAST = lambda shost, mxid: "xmpp_message_bcast/%s/%s" % (shost, mxid)
C_PUB_XMPP_HEARTBEAT = lambda shost, mxid: "xmpp_heartbeat/%s/%s" % (shost, mxid)

S_SUB_XMPP_LOGIN_REQ = lambda shost:"xmpp_login_req/%s/#" % shost
S_SUB_XMPP_LOGOUT_REQ = lambda shost:"xmpp_logout_req/%s/#" % shost
S_SUB_XMPP_ROSTER_ADD_REQ = lambda shost:"xmpp_roster_add_req/%s/#" % shost
S_SUB_XMPP_ROSTER_DEL_REQ = lambda shost:"xmpp_roster_del_req/%s/#" % shost
S_SUB_XMPP_MESSAGE_SEND = lambda shost:"xmpp_message_send/%s/#" % shost
S_SUB_XMPP_MESSAGE_BCAST = lambda shost:"xmpp_message_bcast/%s/#" % shost
S_SUB_XMPP_HEARTBEAT = lambda shost:"xmpp_heartbeat/%s/#" % shost

"""
SERVER 2 CLIENT
"""

S_PUB_XMPP_LOGIN_RES = lambda jid: "xmpp_login_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_LOGOUT_RES = lambda jid: "xmpp_logout_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_ROSTER_NOTIFY = lambda jid: "xmpp_roster_notify/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_ROSTER_PRESENCE_NOTIFY = lambda jid: "xmpp_roster_presence_notify/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_ROSTER_ADD_RES = lambda jid: "xmpp_roster_add_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_ROSTER_DEL_RES = lambda jid: "xmpp_roster_del_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_ROSTER_UPDATE_NOTIFY = lambda jid: "xmpp_roster_update_notify/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_MESSAGE_RES = lambda jid: "xmpp_message_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_MESSAGE_BCAST_RES = lambda jid: "xmpp_message_bcast_res/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_MESSAGE_NOTIFY = lambda jid: "xmpp_message_notify/%s" % JidMgr().get_jid_str(jid)
S_PUB_XMPP_HEARTBEAT_RES = lambda jid: "xmpp_heartbeat_res/%s" % JidMgr().get_jid_str(jid)


C_SUB_XMPP_LOGIN_RES = lambda jid: "xmpp_login_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_LOGOUT_RES = lambda jid: "xmpp_logout_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_ROSTER_NOTIFY = lambda jid: "xmpp_roster_notify/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_ROSTER_PRESENCE_NOTIFY = lambda jid: "xmpp_roster_presence_notify/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_ROSTER_ADD_RES = lambda jid: "xmpp_roster_add_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_ROSTER_DEL_RES = lambda jid: "xmpp_roster_del_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_ROSTER_UPDATE_NOTIFY = lambda jid: "xmpp_roster_update_notify/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_MESSAGE_RES = lambda jid: "xmpp_message_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_MESSAGE_BCAST_RES = lambda jid: "xmpp_message_bcast_res/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_MESSAGE_NOTIFY = lambda jid: "xmpp_message_notify/%s/#" % JidMgr().get_jid_str(jid)
C_SUB_XMPP_HEARTBEAT_RES = lambda jid: "xmpp_heartbeat_res/%s/#" % JidMgr().get_jid_str(jid)
