#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head


@prepend_head
def encode(tid, uid, sms_body):
    """

    :param tid:
    :param uid:
    :param sms_body:
    :return:
    """
    if 20 != len(tid):
        raise ValueError('term_id invalid: %s' % tid)
    if len(sms_body) > 140:
        raise ValueError('sms_body too long: %r' % sms_body)
    return redis_encode_batch(tid, uid, sms_body)