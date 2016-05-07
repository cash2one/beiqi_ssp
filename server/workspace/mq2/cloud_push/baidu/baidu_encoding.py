#coding:utf-8

import time
from urlparse import urljoin
from Crypto.Hash import MD5
import urllib


DEFAULT_HOST = 'http://channel.api.duapp.com/rest/2.0/channel/'
DEFAULT_CHANNEL_CMDS = ('push_msg', 'set_tag', 'fetch_tag', 'delete_tag', 'query_user_tags')


def sign(http_method, url, api_key, secret_key, **kwargs):
    """
    :param http_method: GET|POST
    :param url: 包括http，但不包括参数部分
    :param kwargs: 请求参数对
    """
    _ = url.find('?')
    if -1 != _:
        url = url[:_]
    kwargs.update({'apikey': api_key})
    query_str = ''.join(('{0}={1}'.format(k, kwargs.get(k)) for k in sorted(kwargs.iterkeys())))
    return MD5.new(urllib.quote_plus(''.join((http_method, url, query_str, secret_key)))).hexdigest()


def build_url_post_params(api_key, secret_key, d, host=DEFAULT_HOST):
    """
    创建url和post参数
    """
    assert d and isinstance(d, dict)
    assert 'method' in d

    resource = 'channel'
    channel_id = d.pop('channel_id', None)
    if channel_id and d.get('method') not in DEFAULT_CHANNEL_CMDS:
        resource = channel_id

    ts = int(time.time())
    d.update({'timestamp': ts, 'apikey': api_key})
    url = urljoin(host, resource)
    d.update({'sign': sign('POST', url, api_key, secret_key, **d)})
    return url, d


def query_bind_list(user_id, optional=None):
    """
    用户关注：是
    服务器端根据userId, 查询绑定信息
    参数：
        str userId:  用户ID号
        dict optional: 可选参数
    """
    return {
        'method': 'query_bindlist',
        'user_id': user_id,
    }


def push_message(push_type, messages, message_keys, optional=None):
    """
    推送消息
    参数:
        push_type: 推送消息的类型
        messages：消息内容
        message_keys: 消息key
        optional: 可选参数
    """
    #1: user, 2: tag, 3: all
    assert push_type in (1, 2, 3)
    assert messages and isinstance(messages, str)

    args = {
        'method': 'push_msg',
        'push_type': push_type,
        'messages': messages,
        'msg_keys': message_keys,
    }
    if optional is not None:
        args.update(optional)

    if push_type == 1 and not args.get('user_id'):
        raise ValueError('user_id na when push_to_user')
    elif push_type == 2 and not args.get('tag'):
        raise ValueError('tag na when push_to_tag')
    return args


def verify_bind(user_id, optional=None):
    """
    校验userId是否已经绑定
    参数：
        userId:用户id
        optional:可选参数
    """
    return {
        'method': 'verify_bind',
        'user_id': user_id,
    }


def fetch_message(user_id, optional=None):
    """
    根据userId查询消息
    参数：
        userId:用户id
        optional:可选参数
    """
    return {
        'method': 'fetch_msg',
        'user_id': user_id,
    }


def fetch_message_count(user_id, optional=None):
    """
    根据userId查询消息个数
    参数：
        userId:用户id
        optional:可选参数
    """
    return {
        'method': 'fetch_msgcount',
        'user_id': user_id,
    }


def delete_message(user_id, msg_id, optional=None):
    """
    根据userId, msgIds删除消息
    参数：
        userId:用户id
        msgIds:消息id
        optional:可选参数
    返回值：
        成功：python字典； 失败：False
    """
    return {
        'method': 'delete_msg',
        'user_id': user_id,
        'msg_ids': msg_id,
    }


def set_tag(tag_name, optional=None):
    """
    设置消息标签
    tagName:标签
    optional:可选参数
    """
    return {
        'tag': tag_name,
        'method': 'set_tag',
    }


def fetch_tag(optional=None):
    """
    查询消息标签信息
    optional:可选参数
    """
    return {
        'method': 'fetch_tag',
    }


def delete_tag(tag_name, optional=None):
    """
    删除消息标签
    """
    return {
        'method': 'delete_tag',
        'tag': tag_name,
    }


def query_user_tag(user_id, optional=None):
    """
    查询用户相关的标签
    参数：
        userId:用户id
        optional:可选参数
    """
    return {
        'method': 'query_user_tags',
        'user_id': user_id,
    }


def query_device_type(channel_id, optional=None):
    """
    根据channelId查询设备类型
    参数：
        ChannelId:用户Channel的ID号
        optional:可选参数
    """
    return {
        'channel_id': channel_id,
        'method': 'query_device_type'
    }


def init_ioscert(name, description, release_cert, dev_cert, optional=None):
    """
    初始化应用IOS证书
    参数:
        name: 证书名称，最长128字节
        description: 证书描述，最长256字节
        release_cert: 正式版证书内容
        dev_cert: 开发版证书内容
    返回值:
        成功: dict, {"request_id": 123}; 失败: False
    """
    return {
        'method': 'init_app_ioscert',
        'name': name,
        'description': description,
        'release_cert': release_cert,
        'dev_cert': dev_cert,
    }


def update_ioscert(name, description, release_cert, dev_cert, optional=None):
    """
    更新应用IOS证书
    参数:
        name: 证书名称，最长128字节
        description: 证书描述，最长256字节
        release_cert: 正式版证书内容
        dev_cert: 开发版证书内容
    """
    return {
        'method': 'update_app_ioscert',
        'name': name,
        'description': description,
        'release_cert': release_cert,
        'dev_cert': dev_cert,
    }


def delete_ioscert(optional=None):
    """
    删除应用IOS证书
    """
    return {
        'method': 'delete_app_ioscert'
    }


def query_ioscert(optional=None):
    """
    删除应用IOS证书
    参数:
    返回值:
        成功: dict,
        {
            "request_id": 123,
            "response_params": {
                "name": xxx,
                "description": xxx,
                "release_cert": xxx,
                "dev_cert": xxx
            }
        };
        失败: False
    """
    return {'method': 'query_app_ioscert'}