#coding:utf-8

import msgpack


def pack(sourcer, cb, from_, desc, account=None, cancel_push=False, channel=0b11):
    """
    推送频道：
    * app: 比特位0
    * batch：比特1

    :param sourcer: 推送发起方id
    :param cb: 0成功，1进行中，2失败;cmd;sn
    :param from_: 消息来源，0：客户端控制指令下发，1：自定义请求，如sync，2：外部模块，如算法
    :param account: 推送数据从设备来时，默认向id相关所有帐号推送
    :param cancel_push: 取消推送，例如pt30自动打点时不推送
    :param channel: 推送频道，默认app+batch
    """
    if not (cb and isinstance(cb, str)):
        raise ValueError('cb invalid: {0}'.format(cb))
    if not (isinstance(from_, int) and 0 <= from_ <= 2):
        raise ValueError('from_ invalid: {0}'.format(from_))
    if not isinstance(desc, str):
        raise ValueError('desc invalid: {0}'.format(desc))
    if not (account is None or isinstance(account, str)):
        raise ValueError('account invalid: {0}'.format(account))

    return msgpack.packb(
        {
            'p': {
                'description': desc,
                'id': sourcer,
                'cb': cb,
                'f': from_
            },
            'account': account,
            'cancel': cancel_push,
            'ch': channel,
        }, use_bin_type=True)
