#coding:utf-8


from util.convert import redis_encode_batch
from . import prepend_head


@prepend_head
def encode(api_key, target_id, push_payload):
    """
    长连接推送协议编码
    :param api_key: 开发者帐号
    :param target_id: 目标设备id
    :param push_payload:
    """
    return redis_encode_batch(api_key, target_id, push_payload)


def mq_port_via_push(push_port):
    """
    mq接口与推送服务器的端口关系
    :param push_port: 推送端口
    :return:
    """
    return push_port - 1000


def set_out_proc(api_key, target_id, host, port):
    """
    设置进程外端口
    :param api_key: 开发者key
    :param target_id: 目标设备id
    :param host:
    :param port:
    :return:
    """
    return 'set', ':'.join((api_key, target_id)), ':'.join((host, str(port)))


def get_out_proc(api_key, target_id):
    """
    先找到api_key&target_id所在主机和端口
    mq连接成功后，推送服务器在进程内部查找对应连接
    :param api_key: 开发者key
    :param target_id: 目标设备id
    :return:
    """
    return 'get', ':'.join((api_key, target_id))