#coding:utf-8


import urllib
from Crypto.Hash import MD5
from baidu_encoding import query_device_type, push_message, build_url_post_params
from utils import logger
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.gen import coroutine
from util.torn_resp import json
import time
from auth_keys import baidu_api_info as api_info


http_client = CurlAsyncHTTPClient()


def gen_push_params(appid, api_key, secret_key, push_body_dict, user_id, channel_id, device_type_ob):
    """
    :param device_type_ob: 设备类型对象
    """
    device_type = device_type_ob.get('response_params').get('device_type')
    opts = {
        'user_id': user_id,
        'channel_id': channel_id,
    }
    if 3 == device_type:
        opts.update({'message_type': 0})
    elif 4 == device_type:
        #ios
        opts.update({'message_type': 1})
        #1: develop, 2: release
        opts.update({'deploy_status': 2})
        push_body_dict.update({
            'aps': {
                'alert': push_body_dict.get('description'),
                'sound': 'Voicemail.caf',
                'badge': 1
            },
        })
    return build_url_post_params(api_key, secret_key,
                                 push_message(1, json.dumps(push_body_dict), MD5.new(
                                     'beiqi_key' + str(int(time.time()))).hexdigest(), opts))


@coroutine
def invoke(push_body, channel_args):
    """
    :param channel_args: 百度频道参数
    """
    try:
        _, appid, user_id, channel_id = channel_args
        api_key, secret_key = api_info.get(appid)

        #最多重试3次
        for _ in xrange(3):
                logger.debug('trying push2baidu %d' % _)
                url, dev_params = build_url_post_params(api_key, secret_key, query_device_type(channel_id))
                dev_type_resp = yield http_client.fetch(HTTPRequest(url, method='POST', body=urllib.urlencode(dev_params)))
                logger.debug('get dev_type: {0}'.format(dev_type_resp.body))

                push_url, push_params = gen_push_params(appid, api_key, secret_key, push_body, user_id, channel_id,
                                                        json.loads(dev_type_resp.body))
                push_resp = yield http_client.fetch(
                    HTTPRequest(push_url, method='POST', body=urllib.urlencode(push_params)))
                logger.debug('pbaidu ok: {0} -> {1}'.format(user_id, push_resp.body))
                break
    except Exception, ex:
            logger.error('pbaidu fail: {0}'.format(ex), exc_info=True)
