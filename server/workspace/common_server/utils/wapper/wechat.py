#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-17

@author: Jay
"""
import xmltodict
from utils import logger
from utils.wapper.catch import except_adaptor
from utils.wechat.WXBizMsgCrypt import WXBizMsgCrypt
from utils.wechat.ierror import WXBizMsgCrypt_OK
from utils.service_control.cacher import ParamCacher
from interfaces.service_mgr.tcp_rpc import get_wc_openid


def wechat_recv_wapper(signature_checker, token, encodingAESKey, appid):
    """
    xmpp send 发送适配器
    :param token: 公众平台上，开发者设置的Token
    :param encodingAESKey: 公众平台上，开发者设置的EncodingAESKey
    :param appid: 企业号的AppId
    """
    def wechat_recv_func_wapper(fun):
        @except_adaptor()
        def wechat_recv_param_wapper(self, *args, **kwargs):
            if not signature_checker(token,
                                     kwargs['timestamp'],
                                     kwargs['nonce'],
                                     kwargs['signature']):
                logger.error("wechat_recv_wapper, failed, access_token:%s args:%s, kwargs:%s" %
                             (token, args, kwargs))
                return "-1"

            # 如果没有内容尽是验证，则即可返回
            if not self.request.body:
                return kwargs.get("echostr", "0")

            # 内容解析
            crypt = WXBizMsgCrypt(token, encodingAESKey, appid)
            ret, xml_body = crypt.DecryptMsg(self.request.body,
                                               kwargs['msg_signature'],
                                               kwargs['timestamp'],
                                               kwargs['nonce'])
            assert ret == WXBizMsgCrypt_OK

            order_dic_body = xmltodict.parse(xml_body)
            dic_body = dict(order_dic_body["xml"])
            kwargs['body'] = dic_body

            logger.info("%s:wechat_recv_wapper args:%s kwargs:%s" % (fun.__name__, args, kwargs))
            fun(self, *args, **kwargs)
            return kwargs.get("echostr", "0")
        return wechat_recv_param_wapper
    return wechat_recv_func_wapper


def wechat_get_openid_wapper():
    """
    xmpp send 发送适配器
    """
    def wechat_get_openid_fun_wapper(fun):
        @except_adaptor()
        def wechat_get_openid_param_wapper(*args, **kwargs):
            logger.info("%s:wechat_get_openid_wapper args:%s kwargs:%s" % (fun.__name__, args, kwargs))
            code = kwargs.pop("code", None)
            state = kwargs.pop("state", None)
            assert code
            openid = get_wc_openid(ParamCacher().sm_rpc, code)
            assert openid
            """
            由于openfire不支持用户名大写：有大写的话，roster关系表会转化成小写
            所以将openid转化为小写
            """
            kwargs['openid'] = openid.lower()

            return fun(*args, **kwargs)
        return wechat_get_openid_param_wapper
    return wechat_get_openid_fun_wapper
