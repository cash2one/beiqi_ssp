# coding: utf-8

import time
# from util.log_util import gen_log

TIMELINE_INBOX = 'moments:inbox'
COMMENT_GROUP = 'comment_group'
SHARE_INFO = 'share_info'
COMMENT_INFO = 'comment_info'
SELF_SHARE_PAGE = 'self_share_page'
LIKE_LIST = 'like_list'


def add_self_share(username, ts, share_id):
    return 'hsetnx', ':'.join((SELF_SHARE_PAGE, username)), ts, share_id


def get_all_self_share(username):
    return 'hgetall', ':'.join((SELF_SHARE_PAGE, username))


def del_all_self_share(username):
    return 'delete', ':'.join((SELF_SHARE_PAGE, username))


def add_share(follower, share_id, ts):
    if follower is None or not isinstance(follower, str):
        raise ValueError('add share, follower={0}'.format(follower))
    if share_id is None or not isinstance(share_id, str):
        raise ValueError('add share, share_id={0}'.format(share_id))
    if ts is None or not isinstance(ts, float):
        raise ValueError('add share, type(ts)={0}'.format(type(ts)))

    key = ':'.join((TIMELINE_INBOX, follower))

    return 'zadd', key, share_id, ts


def get_share_by_time(follower, start, end):
    if follower is None or not isinstance(follower, str):
        raise ValueError('get share, follower={0}'.format(follower))
    if start is None or not isinstance(start, float):
        raise ValueError('get share, start={0}'.format(start))
    if end is None or not isinstance(end, float):
        raise ValueError('get share, end={0}'.format(end))

    if start > end or start <= 0 or end <= 0:
        raise ValueError('get share, start={0}, end={1}'.format(start, end))

    key = ':'.join((TIMELINE_INBOX, follower))

    return 'zrangebyscore', key, start, end


def get_share_by_quantity(follower, quantity):
    assert follower and isinstance(follower, str)
    assert quantity and isinstance(quantity, int)

    key = ':'.join((TIMELINE_INBOX, follower))

    return 'zrevrange', key, -1, -1-quantity


def del_share(follower, share_id):
    key = ':'.join((TIMELINE_INBOX, follower))

    return 'zrem', key, share_id


def save_share_info(share_id, author, gid, share_to, location, text, type, files, come_from=''):
    if (share_id and author and gid and share_to and location and text and type and files) is None:
        raise ValueError('save share info, arg None')

    key = ':'.join((SHARE_INFO, share_id))

    mapping = {
        'author': author,
        'gid': gid,
        'share_to': share_to,
        'location': location,
        'text': text,
        'type': type,
        'files': files,
        'from': come_from,
        # 'attachments': attachments
    }

    return 'hmset', key, mapping


def retrieve_share_info(share_id):
    key = ':'.join((SHARE_INFO, share_id))
    return 'hgetall', key


def del_share_info(share_id):
    key = ':'.join((SHARE_INFO, share_id))
    return 'delete', key


def add_comment(share_id, comment_id):
    if share_id is None or not isinstance(share_id, str):
        raise ValueError('add comment, share_id={0}'.format(share_id))
    if comment_id is None or not isinstance(comment_id, str):
        raise ValueError('add comment, comment_id={0}'.format(comment_id))

    key = ':'.join((COMMENT_GROUP, share_id))
    score = comment_id.split(':')[-2]

    return 'zadd', key, comment_id, score


def get_comment(share_id):
    if share_id is None or not isinstance(share_id, str):
        raise ValueError('get comment, share_id={0}'.format(share_id))

    start = share_id.split(':')[1]
    now = round(time.time(), 2)
    key = ':'.join((COMMENT_GROUP, share_id))

    # gen_log.debug('get comment, share_id={0}, start={1}, now={2}, key={3}'.format(share_id, start, now, key))

    return 'zrangebyscore', key, start, now


def del_comment(share_id):
    key = ':'.join((COMMENT_GROUP, share_id))

    return 'delete', key


def del_one_comment(share_id, comment_id):
    key = ':'.join((COMMENT_GROUP, share_id))

    return 'zrem', key, comment_id


def save_comment_info(share_id, new_comment_id, reply_to, comment_id, text, type, file):
    if (share_id and comment_id) is None:
        raise ValueError('save comment info share_id={0}, comment_id={0}'.format(share_id, comment_id))
    if (text or (type and file)) is None:
        raise ValueError('save comment info text={0}, type={1}, file={2}'.format(text, type, file))

    key = ':'.join((COMMENT_INFO, share_id, new_comment_id))

    mapping = {
        'reply_to': reply_to,
        'comment_id': comment_id,
        'text': text,
        'type': type,
        'file': file
        }

    return 'hmset', key, mapping


def retrieve_comment_info(share_id, comment_id):
    key = ':'.join((COMMENT_INFO, share_id, comment_id))

    return 'hgetall', key


def del_comment_info(share_id, comment_id):
    key = ':'.join((COMMENT_INFO, share_id, comment_id))

    return 'delete', key


def get_comment_file(share_id, comment_id):
    key = ':'.join((COMMENT_INFO, share_id, comment_id))

    return 'hget', key, 'file'


def add_like(share_id, account):
    if (share_id and account) is None or not isinstance(share_id, str) or not isinstance(account, str):
        raise ValueError('add like, share_id={0}, account={1}'.format(share_id, account))

    return 'rpush', ':'.join((LIKE_LIST, share_id)), account


def get_like(share_id):
    if share_id is None or not isinstance(share_id, str):
        raise ValueError('get like, share_id={0}'.format(share_id))

    return 'lrange', ':'.join((LIKE_LIST, share_id)), 0, -1


def cancel_like(share_id, account):
    if (share_id and account) is None or not isinstance(share_id, str) or not isinstance(account, str):
        raise ValueError('cancel like, share_id={0}, account={1}'.format(share_id, account))

    return 'lrem', ':'.join((LIKE_LIST, share_id)), account
