#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head
import msgpack


@prepend_head
def encode(push_alert, push_custom_payload, compile_type, bundle_id, device_token):
    """
    水果推送协议编码
    :param push_alert: 水果推送标题
    """
    if not (push_alert and isinstance(push_alert, str)):
        raise ValueError('alert not str: %s' % type(push_alert))
    if not (push_custom_payload and isinstance(push_custom_payload, dict)):
        raise ValueError('payload not dict: %s' % type(push_custom_payload))

    # payload = {
    #     'aps': {
    #         'alert': push_alert,
    #         'badge': 1,
    #         'sound': 'Voicemail.caf'
    #     }
    # }
    payload = {
        'aps': {
            'content-available': 1,
            'data': push_alert,
        }
    }
    payload.update(push_custom_payload)
    payload = msgpack.packb(payload, use_bin_type=True)

    return redis_encode_batch(compile_type, bundle_id, device_token, payload)