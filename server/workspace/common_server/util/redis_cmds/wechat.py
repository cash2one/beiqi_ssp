#coding: utf8


WECHAT_ACCESS_TOKEN = 'wechat_access_token'
WECHAT_TICKET = 'wechat_ticket'

def get_wechat_access_token():
    return 'get', WECHAT_ACCESS_TOKEN


def set_wechat_access_token(token, expires):
    return ('set', WECHAT_ACCESS_TOKEN, token, int(expires))


def get_wechat_ticket():
    return 'get', WECHAT_TICKET


def set_wechat_ticket(ticket, expires):
    return ('set', WECHAT_TICKET, ticket, int(expires))
