# coding: utf-8
from tornado.gen import coroutine
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest
from utils import logger
import hashlib
import time

http_client = CurlAsyncHTTPClient()


SEND_SMS_URL = 'http://userinterface.vcomcn.com/Opration.aspx'

VCOM_ACCOUNT = 'xmbqkj'
VCOM_PWD = 'XMbq963'
CHARSET = 'gb2312'


def build_auth(user_id, acc, pwd):
    """
    认证串构建
    :param user_id:
    :param acc:
    :param pwd:
    :return:
    """
    return 'action=send&userid={0}&account={1}&password={2}&mobile='.format(user_id, acc, pwd)


def build_sign(s):
    """
    签名串
    :param s:
    :return:
    """
    return '【{0}】'.format(s)


def get_pwd_md5():
    m = hashlib.md5()
    m.update(VCOM_PWD)
    return m.hexdigest().upper()


@coroutine
def vcomcn_sms(tel, body):
    """
    上海集时通
    :param auth_str: 认证串
    :param sign:
    :param mobile:
    :param body:
    """

    content_type = 'text/xml'
    headers = {'content_type': content_type, 'charset': CHARSET}

    content = '<Group Login_Name="' + VCOM_ACCOUNT + '" Login_Pwd="' + get_pwd_md5() + '" OpKind="0" InterFaceID="0">\r\n' + \
    '<E_Time></E_Time>\r\n' + \
    '<Item>\r\n' + \
    '<Task>\r\n' + \
    '<Recive_Phone_Number>' + tel + '</Recive_Phone_Number>\r\n' + \
    '<Content>' + body.decode('utf8').encode('gb2312') + '</Content>\r\n' + \
    '<Search_ID>' + ':'.join((tel, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))) + '</Search_ID>\r\n' + \
    '</Task>\r\n' + \
    '</Item>\r\n' + \
    '</Group>\r\n'

    try:
        resp = yield http_client.fetch(HTTPRequest(SEND_SMS_URL, method='POST', headers=headers, body=content))
        logger.debug('vcomcn remains: code={0}, body={1}'.format(resp.code, resp.body))
    except Exception as ex:
        logger.error('vcomcn sms error: {0}'.format(ex, exc_info=True))
