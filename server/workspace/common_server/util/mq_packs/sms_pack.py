# coding:utf-8


import re
import msgpack
from util.convert import is_cdma_tid
from util.crypto_rc4 import encrypt as rc4_encrypt
from base64 import standard_b64encode


def encode_sms(code, cb, sn, attr, session_key, with_plain=False):
    """
    编码设备短信
    :param code:
    :param cb:
    :param sn:
    :param attr:
    :param session_key:
    :param with_plain: 同时返回明文
    :return:
    """
    plain = '|'.join((code, ':'.join((cb, str(sn))), attr))
    cipher = rc4_encrypt(plain, session_key, standard_b64encode)
    if not with_plain:
        return cipher
    return cipher, plain


def pack(pid, biz_token, terminal_id, body, cb):
    """
    编码短信mq消息
    :param biz_token: 业务token
    :param terminal_id: sms终端id
    :param body:
    """
    if not (body and isinstance(body, str) and len(body) <= 140):
        raise ValueError('dev sms body invalid: %s' % type(body))

    return msgpack.packb(
        {
            'pid': pid,
            'n': terminal_id,
            'p': body,
            'uid': biz_token,
            'cb': cb,
        }, use_bin_type=True
    )