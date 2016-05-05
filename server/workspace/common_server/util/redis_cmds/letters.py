# coding:utf8


LETTER_INBOX = 'letter_inbox'
LETTER_OUTBOX = 'letter_outbox'
LETTER_INFO = 'letter_info'


def add_letter_outbox(sender, letter_id, ts):
    return 'zadd', ':'.join((LETTER_OUTBOX, sender)), letter_id, ts


def add_letter_inbox(receiver, letter_id, ts):
    return 'zadd', ':'.join((LETTER_INBOX, receiver)), letter_id, ts


def get_letter_inbox(user, start, end):
    return 'zrevrange', ':'.join((LETTER_INBOX, user)), start, end


def del_letter_inbox(user, letter_id):
    return 'zrem', ':'.join((LETTER_INBOX, user)), letter_id


def save_letter_info(letter_id, letter_info):
    return 'hset', LETTER_INFO, letter_id, letter_info


def get_letter_info(letter_id):
    return 'hget', LETTER_INFO, letter_id


def del_letter_info(letter_id):
    return 'hdel', LETTER_INFO, letter_id