#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-7

@author: Jay
"""
from interfaces.sso_server.http_rpc import gen_tk
from utest_lib.setting import TEST_USER_NAME, TEST_PASSWD
from utest_lib.service import SSOHttpRpcClt
from util.oem_account_key import APP_KEY
from interfaces.dev_server.http_rpc import sign_in
from utest_lib.setting import TEST_SN, SERVER_IP, DEV_SERVER_PORT
from util.sso_common.build_sso_token import encrypt_username
from util.oem_account_key import DEV_KEY, DEV_RC4, DEV_SECRET, APP_SECRET
from interfaces.api_server.http_rpc import add_device


def gen_test_tk(user_name=TEST_USER_NAME, pwd=TEST_PASSWD, app_key=APP_KEY, dev_rc4=DEV_RC4):
    return gen_tk(SSOHttpRpcClt, user_name , pwd, app_key, dev_rc4)

# Éè±¸µÇÂ¼+°ó¶¨
dev_tk = gen_test_tk(encrypt_username(TEST_SN, DEV_RC4), app_key=DEV_KEY, dev_rc4=DEV_RC4)
sign_in_res = sign_in(SERVER_IP, dev_tk, DEV_SECRET, TEST_SN, DEV_SERVER_PORT)
print "sign_in_res,",sign_in_res
GDevGid = sign_in_res['gid']
GDevIC = sign_in_res.get('ic', None)
if GDevIC:
    add_device_res = add_device(SERVER_IP, gen_test_tk(), APP_SECRET, code=GDevIC)
    print "add_device_res,",add_device_res


