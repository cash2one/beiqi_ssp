#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/18

@author: Jay
"""
import base64
from binascii import b2a_hex, a2b_hex
import struct
import time
from convert import pad, unpad, bs2utf8
from bit import span_bits
from crypto_rc4 import encrypt as rc4_encrypt, decrypt as rc4_decrypt
import random
from utils import logger


MAX_FILENAME_LEN = 68
tk_pwd = '9123fa3498d249c5948a4c2fa7d29a39'
ref_pwd = '6ee41d12de5745b1bf23b15ef508c7a4'
fn_pwd = '7941010ea9a94e62952c3c5407390014'


def gen_file_tk_l(acc, fn, ul, by_app):
    """
    生成文件服务器访问token:长字符串

    :param acc: 设备id
    :param fn: 文件名
    :param ul: 上传
    :param by_app: 数据由app产生
    :param share: 是否可被多人访问
    """
    fn = bs2utf8(fn)

    if not (acc and isinstance(acc, str)):
        return 1
    if not (fn and isinstance(fn, str)):
        return 2

    share = 1
    #是否共享，app产生，主帐号，上传/下载
    head = struct.pack('>BB', ((int(share) << 7) | (int(by_app) << 6) | (int(ul) << 5)),
                       len(acc))
    rnd = random.randint(0, 126)
    val = rnd + 1
    rnd = struct.pack('>B', rnd)
    val = rc4_encrypt(struct.pack('>B', val), tk_pwd, None)

    _ = ''.join((head,
                 acc,
                 struct.pack('>I', int(time.time())),
                 pad(fn, MAX_FILENAME_LEN),
                 rnd,
                 val))
    return rc4_encrypt(_, tk_pwd, b2a_hex)


def gen_file_tk_s(acc, fn, ul, by_app):
    """
    生成文件服务器访问token：短字符串

    :param acc: 设备id
    :param fn: 文件名
    :param ul: 上传
    :param by_app: 数据由app产生
    """
    fn = bs2utf8(fn)
    acc = str(acc)
    fn = str(fn)

    share = 1
    #是否共享，app产生，主帐号，上传/下载
    head = struct.pack('>BB', ((int(share) << 7) | (int(by_app) << 6) | (int(ul) << 5)), len(acc))
    b64str = base64.b64encode(''.join((head, acc, struct.pack('>I', int(time.time())), fn)))
    return b64str


def gen_ref_l(share, by_app, acc, fn):
    """
    生成凭据
    :param acc: pid或者account：长字符串
    """
    if not (acc and isinstance(acc, str)):
        return None
    if not (fn and isinstance(fn, str)):
        return None

    key_cipher = rc4_decrypt(acc, ref_pwd, None)
    head = struct.pack('>BBB', ((int(share) << 7) | (int(by_app) << 6)), len(acc),
                       len(key_cipher))
    _ = ''.join((head,
                 acc,
                 key_cipher,
                 pad(fn, MAX_FILENAME_LEN)))
    return rc4_encrypt(_, ref_pwd, b2a_hex)


def gen_ref_s(share, by_app, acc, fn):
    """
    生成凭据
    :param acc: pid或者account：短字符串
    """
    acc = str(acc)
    fn = str(fn)
    head = struct.pack('>BB', ((int(share) << 7) | (int(by_app) << 6)), len(acc))
    b64str = base64.b64encode(''.join([head, acc, fn]))
    return b64str


def extract_ref_l(ref):
    """
    解析ref：长字符串
    :param ref:
    :return:
    """
    logger.debug('extract ref begin')

    if not ref or not isinstance(ref, str) or ref == '':
        return None
    ref = rc4_decrypt(ref, ref_pwd, a2b_hex)
    logger.debug(u'ref = %r', ref)
    if len(ref) <= 3:
        #至少要求3字节
        return None

    head, acc_len, key_cipher_len = struct.unpack('>BBB', ref[:3])
    logger.debug(u'head = %r, acc_len = %r, key_cipher_len = %r', head, acc_len, key_cipher_len)
    if len(ref) != 3 + acc_len + key_cipher_len + MAX_FILENAME_LEN:
        return None

    acc = ref[3:acc_len + 3]
    key_cipher = ref[acc_len + 3:acc_len + 3 + key_cipher_len]
    logger.debug(u'acc = %r, key_cipher = %r', acc, key_cipher)
    logger.debug(u'rc4 decrypt result = %r', rc4_decrypt(key_cipher, ref_pwd, None))
    if acc != rc4_decrypt(key_cipher, ref_pwd, None):
        return None

    share, by_app = span_bits(head, 7, 6, 0)

    logger.debug('extract ref end')

    return share, by_app, acc, unpad(ref[-MAX_FILENAME_LEN:])


def extract_ref_s(ref):
    """
    解析ref：短字符串
    :param ref:
    :return:
    """
    b64str = base64.b64decode(str(ref))
    head, acc_len = struct.unpack('>BB', b64str[:2])
    share, by_app = span_bits(head, 7, 6, 0)
    return share, by_app, b64str[2:acc_len + 2], b64str[acc_len + 2:]


def extract_tk_l(tk, ul):
    """
    :param ul: 上传：长字符串
    """
    logger.debug('extract tk begin')
    if not tk or not isinstance(tk, str) or len(tk) <= 2:
        logger.info('tk too short')
        return None
    tk = rc4_decrypt(tk, tk_pwd, a2b_hex)
    logger.debug(u'tk = %r', tk)
    rnd, val = tk[-2:]
    val = rc4_decrypt(val, tk_pwd, None)
    logger.debug('rnd = %r, val = %r', rnd, val)
    rnd = struct.unpack('>B', rnd)[0]
    val = struct.unpack('>B', val)[0]
    logger.debug('rnd = %r, val = %r', rnd, val)

    if rnd + 1 != val:
        logger.warn('rnd={0} & val={1} unmatch'.format(rnd, val))
        return None

    head, acc_len = struct.unpack('>BB', tk[:2])
    logger.debug('head = %r, acc_len = %r', head, acc_len)
    if len(tk) != 2 + acc_len + 4 + MAX_FILENAME_LEN + 2:
        logger.warn('tk len not ok')
        return None

    #10分钟有效
    ts_offset = 2 + acc_len
    t = struct.unpack('>I', tk[ts_offset:ts_offset+4])[0]
    now = time.time()
    logger.debug('now = %r, t = %r', now, t)

    if now - struct.unpack('>I', tk[ts_offset:ts_offset+4])[0] >= 600:
        logger.warn('tk timeout')
        logger.debug('now = %r, t = %r', now, t)
        return None

    share, by_app, is_ul = span_bits(head, 7, 5, 0)
    logger.debug('share = %r, by_app = %r, is_ul = %r, ul=%r', share, by_app, is_ul, ul)
    if is_ul != ul:
        logger.warn('ul param invalid')
        return None

    logger.debug('extract tk end')

    return share, by_app, tk[2: acc_len+2], unpad(tk[ts_offset+4: ts_offset+4+MAX_FILENAME_LEN])


def extract_tk_s(tk, ul):
    """
    :param ul: 上传：短字符串
    """
    b64str = base64.b64decode(str(tk))
    head, acc_len = struct.unpack('>BB', b64str[:2])
    share, by_app, is_ul = span_bits(head, 7, 5, 0)

    #10分钟有效
    ts_offset = 2 + acc_len
    t = struct.unpack('>I', b64str[ts_offset:ts_offset+4])[0]
    if time.time() - t >= 600:
        return None
    return share, by_app, b64str[2: acc_len+2], b64str[ts_offset+4:]


def check_tk_ref(tk, ul, ref):
    """
    :param ul: 上传
    """
    tk = extract_tk(tk, ul)
    if not tk:
        return None
    ref = extract_ref(ref)
    if not ref:
        return None
    logger.debug('check_tk_ref tk={0}, ref={1}'.format(tk, ref))
    if len(tk) != len(ref):
        return None
    #api/file_tk返回的unique_token为pid
    #英语单词构造的为其他
    # 以下逻辑暂时不处理，不知道干什么，jay
    #for index in (0, 1, 3):
    #    if tk[index] != ref[index]:
    #        return None
    return ref


def gen_lvl_fn(share, by_app, acc, fn):
    """
    生成lvl文件名
    :param acc: id和account都可接受
    """
    if not (acc and isinstance(acc, str) and len(acc) <= 0xff):
        return None
    if not (fn and isinstance(fn, str)):
        return None

    first = struct.pack('>BB', ((int(share) << 7) | (int(by_app) << 6)), len(acc))
    return rc4_encrypt(''.join((first, acc, pad(fn, MAX_FILENAME_LEN))), fn_pwd, b2a_hex)


def is_fn_ok(fn):
    if not fn or not isinstance(fn, str):
        return False
    return True


def gen_file_tk(acc, fn, ul, by_app):
    try:
        return gen_file_tk_s(acc, fn, ul, by_app)
    except:
        return gen_file_tk_l(acc, fn, ul, by_app)


def extract_tk(tk, ul):
    try:
        return extract_tk_s(tk, ul)
    except:
        return extract_tk_l(tk, ul)


def gen_ref(share, by_app, acc, fn):
    try:
        return gen_ref_s(share, by_app, acc, fn)
    except:
        return gen_ref_l(share, by_app, acc, fn)


def extract_ref(ref):
    try:
        return extract_ref_s(ref)
    except:
        return extract_ref_l(ref)


if __name__ == '__main__':
    ref = gen_ref(True, True, 'c2000018', 'abcde')
    assert extract_ref(ref)

    tk = gen_file_tk('c2000018', 'abcde', True, True, True)
    print tk
    print extract_tk(tk, True)
    print check_tk_ref(tk, True, ref)

