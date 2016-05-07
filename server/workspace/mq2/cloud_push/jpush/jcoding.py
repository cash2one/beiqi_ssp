#coding:utf-8

from utils import logger
from util.torn_resp import json
from tornado.httpclient import HTTPRequest
from auth_keys import jpush_api_info as api_info


url = 'https://api.jpush.cn/v3/push'


def build_req(push_body, channel_args):
    if 3 != len(channel_args):
        logger.warn('jpush args invalid: {0}'.format(channel_args))
        return

    _, api_key, reg_id = channel_args
    secret = api_info.get(api_key)
    if not secret:
        logger.warn('jpush key {0} not found'.format(api_key))
        return

    desc = push_body.get('description', '')
    push_body.pop('title', None)
    ios_extras = dict(push_body)
    ios_extras.pop('description', None)
    payload = {
        'platform': 'all',
        'audience': {'registration_id': [reg_id]},
        'message': {
            'msg_content': desc,
            'extras': push_body,
        },
        "notification": {
            "ios": {
                "alert": desc,
                "sound": "Voicemail.caf",
                "badge": 1,
                "extras": ios_extras
            }
        },
        "options": {
            "apns_production": True
        }
    }
    return HTTPRequest(
        url,
        auth_username=api_key,
        auth_password=secret,
        auth_mode='basic',
        method='POST',
        body=json.dumps(payload, separators=(',', ':')),
        validate_cert=False,
    )
