#coding:utf-8


import time
from util.crypto_rc4 import encrypt as rc4_encrypt
from util.crypto_rc4 import decrypt as rc4_decrypt
from utils import logger
from util.sso.account import set_login_expire

# SSO_KEY = 'd15d67922dd241cdbfc355d19544d6757dc759e60b3c4b74b868704c8a37b897'
SSO_KEY = 'e91647cf091a11e69e11408d5c5a48caf4393b8f091a11e6bb44408d5c5a48ca'

tbl_name = 'device_info'

def gen_token(api_secret, username, expire_days, api_key=None, account_rds=None):
    """
    获取token
    :param api_secret:
    :param username:
    :param expire_days:
    :param api_key:
    :param account_rds:
    :return:
    """
    expire = 'exp:{0}'.format(int(time.time() + 86400 * expire_days))
    secret = 'sec:{0}'.format(api_secret)
    account = 'acc:{0}'.format(username)

    head = 'pkey:{0}'.format(api_key[:4]) if api_key else None
    l = [expire, secret, account]
    if head:
        l.append(head)

    plain = '|'.join(l)
    logger.debug('gen token, plain: {0}, token: {1}'.format(plain, rc4_encrypt(plain, SSO_KEY)))

    # _account_cache.send_cmd(*set_login_expire(username, expire.split(':')[1]))
    if account_rds:
        account_rds.execute([set_login_expire(username, expire.split(':')[1])])

    del l
    return rc4_encrypt(plain, SSO_KEY)


def parser_token(token):
    """
    解析token
    :param token: token
    :return: api_secret, username, expire_days,
    """
    plain = rc4_decrypt(token, SSO_KEY)

    plain_ls = [v.split(":")[1] for v in  plain.split("|")]
    if len(plain_ls) == 4:
        expire, secret, account, api_key = plain_ls
    else:
        expire, secret, account = plain_ls
        api_key = ""
    return int(expire), secret, account,  api_key


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

