#coding:utf-8


import urllib
from Crypto.Hash import MD5
from utils import logger
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.gen import coroutine
from util.torn_resp import json
import time
import json
from jcoding import build_req


http_client = CurlAsyncHTTPClient()
limit_keys = ('X-Rate-Limit-Limit', 'X-Rate-Limit-Remaining', 'X-Rate-Limit-Reset')


@coroutine
def invoke(push_body, channel_args):
    try:
        http_req = build_req(push_body, channel_args)
        if not http_req:
            return
        resp = yield http_client.fetch(http_req)
        limit_dict = dict(((k, int(resp.headers.get(k, '0'))) for k in limit_keys))
    except Exception, ex:
        logger.error('jpush fail: {0}'.format(ex))
