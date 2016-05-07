#coding:utf-8


from utils import logger
from tornado.gen import coroutine
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest
from util.torn_resp import json


google_client = CurlAsyncHTTPClient()
GOOGLE_AUTH_KEY = 'AIzaSyCC3KbtTjszGQ1-yU45geoHCedWM9u8Ce0'
GOOGLE_URL = 'https://android.googleapis.com/gcm/send'


@coroutine
def invoke(push_body, channel_args):
    """
    :param push_body: dict
    :param channel_args: 频道参数
    """
    body = {
        'data': push_body,
        'registration_ids': channel_args,
    }

    resp = yield google_client.fetch(HTTPRequest(GOOGLE_URL, method='POST', headers={
        'Authorization': 'key={0}'.format(GOOGLE_AUTH_KEY),
        'Content-Type': 'application/json',
    }, body=json.dumps(body, separators=(',', ':'))))

    logger.debug('GOOG resp: {0}'.format(resp.body))