#coding:utf-8


"""
苹果推送共有3种协议格式：
0) simple notification format
1) enhanced notification format
3) modern format <-- 苹果官方文档推荐使用，但浪费字节数更多

v0和其他的区别在于：
1) v0不支持identifier应答查询，因为发送报文中无该字段
2) v0占用无效字节数最小
"""

import time
import re
import binascii
import struct
import json
from utils import logger


DEVICE_TOKEN_PATTERN = re.compile(r'^[a-f\d]{64}$')
PAYLOAD_MAXLEN = 2047
ITEM_MAXLEN = 2047
FEEDBACK_UNIT = 10


def v0_encode(device_token, alert_msg):
    """
    :param device_token: 手机从apns服务器获取的64字节
    :param alert_msg: 显示在手机上的提示信息
    """
    if not (device_token and isinstance(device_token, str) and DEVICE_TOKEN_PATTERN.search(device_token)):
        raise ValueError('invalid device_token: %r' % device_token)
    if not (alert_msg and isinstance(alert_msg, str)):
        raise ValueError('invalid alertmsg: %r' % alert_msg)

    payload = json.dumps({'aps': {'alert': alert_msg}}, separators=(',', ':'))
    if len(payload) > PAYLOAD_MAXLEN:
        raise ValueError('v0 payload too long: %d' % len(payload))

    return ''.join((
        #command: 0
        '\x00',
        '\x00 ',
        binascii.a2b_hex(device_token),
        struct.pack('>H', len(payload)),
        payload
    ))


def v1_encode(msg_id, device_token, msg_title, expire=86400, badge=1, sound='', custom_payload=None):
    """
    :param msg_id: 唯一的消息id，在apns有错误应答时会附带该id
    :param expire: 过期时长，0值则不存储，发送成功与否立即丢弃；否则在指定时间内至少重试一次
    """
    if not (msg_id and isinstance(msg_id, int)):
        raise ValueError('msg_id not int, but %s' % type(msg_id))

    expire = int(time.time() + expire) if expire else 0
    payload = {
        'aps': {
            'alert': msg_title,
            'badge': badge,
            'sound': sound,
        }
    }
    if custom_payload and isinstance(custom_payload, dict) and 'aps' not in custom_payload:
        payload.update(custom_payload)
    payload = json.dumps(payload, separators=(',', ':'))
    if len(payload) > PAYLOAD_MAXLEN:
        raise ValueError('v1 payload too long: %d' % len(payload))

    return ''.join((
        '\x01',
        struct.pack('>I', msg_id),
        struct.pack('>I', expire),
        '\x00 ',
        binascii.a2b_hex(device_token),
        struct.pack('>H', len(payload)),
        payload,
    ))
    

def __v2item(item_id, s):
    if not (s and isinstance(s, str) and len(s) <= ITEM_MAXLEN):
        raise ValueError('invalid v2 data: %r' % s)
    return ''.join((struct.pack('>B', item_id), struct.pack('>H', len(s)), s))


def v2_encode(msg_id, device_token, payload, priority=10):
    """
    :param payload: 
    {
        'aps': {
            'alert': alert_msg,
            'badge': badge,
            'sound': sound,
        },
        custom_dict
    }
    :param msg_id: 用于APNs应答错误时使用，区分消息记录
    :param priority: 10立即发送
    
    gateway.sandbox.push.apple.com:2195
    gateway.push.apple.com:2195
    """
    if not (device_token and isinstance(device_token, str) and DEVICE_TOKEN_PATTERN.search(device_token)):
        raise ValueError('invalid device_token: %r' % device_token)
    if not (payload and isinstance(payload, dict) and 'aps' in payload):
        raise ValueError('payload invalid: %s' % payload)
    if not (isinstance(msg_id, int) and msg_id >= 0):
        raise ValueError('notify_id not int: %s' % type(msg_id))

    payload = json.dumps(payload, separators=(',', ':'))
    if len(payload) > PAYLOAD_MAXLEN:
        raise ValueError('v2 payload too long: %d, %s' % (len(payload), payload))

    device_token = binascii.a2b_hex(device_token)
    #过期时间，至少发送一次
    expiry = int(time.time() + 86400)
    
    frame_data = ''.join(
        (
            __v2item(1, device_token),
            __v2item(2, payload),
            __v2item(3, struct.pack('>I', msg_id)),
            __v2item(4, struct.pack('>I', expiry)),
            __v2item(5, struct.pack('>B', priority))
        )
    )
    return ''.join(('\x02', struct.pack('>I', len(frame_data)), frame_data))
    
    
resp_errno = {
    0: 'no err',
    1: 'processing err',
    2: 'missing device token',
    3: 'missing topic',
    4: 'missing payload',
    5: 'invalid token size',
    6: 'invalid topic size',
    7: 'invalid payload size',
    8: 'invalid token',
    10: 'APNs connection closed (performing maintenance e.g)',
    255: 'unknown',
}    
    
    
def err_resp(s):
    if not s:
        return None
    if len(s) < 6:
        return None
    if '\x08' != s[0]:
        logger.warn('apns recv invalid: %r' % s)
        return None

    #错误代码，对应消息id（4字节int）
    return struct.unpack('>BI', s[1:])
    
    
def feedback_resp(s):
    """
    当对应该的app已卸载时，feedback服务会追加该device token
    已过期的推送任务不会追加进来
    
    feedback服务与app是一比一的关系，不同app使用不同证书查询（和推送使用同一证书）
    生产环境：feedback.push.apple.com:2196
    测试：feedback.sandbox.push.apple.com:2196
    一旦连接成功，不用发送任何字节，APNs服务器则开始回写数据流；写完即从APNs服务器删除
    
    4字节时间戳，2字节长度，4字节device token；10字节一组
    """
    #todo: 每日检查feedback列表，根据时间戳确认该app没有重新安装并启动过，则可在推送队列中移除该device token
    if not (s and isinstance(s, str) and len(s) >= FEEDBACK_UNIT):
        return s

    l = []
    block = len(s) / FEEDBACK_UNIT
    for i in xrange(block):
        l.append(struct.unpack('>IHI', s[i * FEEDBACK_UNIT: (i + 1) * FEEDBACK_UNIT]))

    return l, s[block * FEEDBACK_UNIT:]