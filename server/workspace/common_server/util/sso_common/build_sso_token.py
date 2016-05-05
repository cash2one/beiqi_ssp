#coding:utf-8


import time
from util.crypto_rc4 import encrypt as rc4_encrypt
from util.crypto_rc4 import decrypt as rc4_decrypt
from util.log_util import gen_log
from util.sso.account import set_login_expire

# SSO_KEY = 'd15d67922dd241cdbfc355d19544d6757dc759e60b3c4b74b868704c8a37b897'
SSO_KEY = 'e90445b608d940f9a7d114fea3497a4153fdcc315dff41809ad9cb703b53502a'

tbl_name = 'device_info'

#获取token
def gen_token(api_secret, username, expire_days, api_key=None):
    expire = 'exp:{0}'.format(int(time.time() + 86400 * expire_days))
    secret = 'sec:{0}'.format(api_secret)
    account = 'acc:{0}'.format(username)

    head = 'pkey:{0}'.format(api_key[:4]) if api_key else None
    l = [expire, secret, account]
    if head:
        l.append(head)

    plain = '|'.join(l)
    gen_log.debug('gen token, plain: {0}, token: {1}'.format(plain, rc4_encrypt(plain, SSO_KEY)))
    _account_cache.send_cmd(*set_login_expire(username, expire.split(':')[1]))

    del l
    return rc4_encrypt(plain, SSO_KEY)


def decrypt_username(username, key):
    try:
        plain = rc4_decrypt(username, key)
    except Exception, e:
        gen_log.debug('decrypt username failed, username={0}, key={1}'.format(username, key))
        return None

    sn, ts, magic = plain.split('|')
    if magic != 'bq':
        gen_log.debug('magic={0}'.format(magic))
        return None

    return sn, ts

