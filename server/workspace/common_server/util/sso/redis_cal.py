#coding:utf-8


def lock_pt30_sms(pid):
    assert pid and isinstance(pid, str)

    key = ':'.join(('lock_pt30', pid))
    return (('set', key, '1'),
            ('expire', key, 60))


def unlock_pt30_sms(pid):
    assert pid and isinstance(pid, str)
    return 'delete', ':'.join(('lock_pt30', pid))


def is_pt30_sms_locked(pid):
    assert pid and isinstance(pid, str)
    return 'exists', ':'.join(('lock_pt30', pid))


def incre_unique_sn():
    return 'incr', 'sms:sn'