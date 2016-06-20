#coding:utf-8

import binascii
import time
from util.crypto_rc4 import encrypt as rc4_encrypt
from util.crypto_rc4 import decrypt as rc4_decrypt
from utils import logger
from util.sso.account import set_login_expire

SSO_KEY = 'e91647cf091a11e69e11408d5c5a48caf4393b8f091a11e6bb44408d5c5a48ca'

def gen_token(api_secret, username, expire_days, account_rds=None):
    """
    获取token
    :param api_secret:
    :param username:
    :param expire_days:
    :param account_rds:
    :return:
    """
    expire = str(int(time.time()) + 86400 * expire_days)
    plain = '|'.join([expire, api_secret, username])

    if account_rds:
        account_rds.send_cmd(*set_login_expire(username, expire))

    token = rc4_encrypt(plain, SSO_KEY)
    logger.debug('gen token, plain: {0}, token: {1}'.format(plain, token))
    return token


def parser_token(token):
    """
    解析token
    :param token: token
    :return: api_secret, username, expire_days,
    """
    plain = rc4_decrypt(token, SSO_KEY)
    expire, secret, account = plain.split("|")
    return int(expire), secret, account


def decrypt_username(username, key):
    try:
        plain = rc4_decrypt(username, key)
    except Exception, e:
        logger.debug('decrypt username failed, username={0}, key={1}'.format(username, key))
        return None

    sn, ts, magic = plain.split('|')
    if magic != 'bq':
        logger.debug('magic={0}'.format(magic))
        return None

    return sn, ts


def encrypt_username(username, dev_secret):
    plain = '|'.join([username, "%0.2f"% time.time(), "bq"])
    return rc4_encrypt(plain, dev_secret, binascii.b2a_base64)

