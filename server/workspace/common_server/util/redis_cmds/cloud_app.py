#coding:utf8


CLOUD_APP = 'cloud_app'


def set_app_data(receiver, app, now, payload):
    return 'hset', ':'.join((CLOUD_APP, receiver, app)), now, payload


def get_app_data(username, app):
    return 'hgetall', ':'.join((CLOUD_APP, username, app))


def get_app_data_by_ts(username, app, ts):
    return 'hget', ':'.join((CLOUD_APP, username, app)), ts


def del_app_data(username, app, time_index):
    return 'hdel', ':'.join((CLOUD_APP, username, app)), time_index