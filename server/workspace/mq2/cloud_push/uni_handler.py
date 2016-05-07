#coding:utf8
from utils import logger
from util.sso.dev_active import *
from util.redis.redis_client import Redis
from util.stream_config_client import load as conf_load
from util.convert import combine_redis_cmds
from util.bit import span_bits
from . import find_push
from copy import deepcopy


group = dict(conf_load('redis.ini'))
redis_conf = group.get('redis.ini')

redis_cal = Redis(redis_conf.get('calculation', 'url'))
dev_filter = Redis(redis_conf.get('dev_filter', 'url'))
account_cache = Redis(redis_conf.get('oauth', 'url'))


def handle_pid_account(account):
    if len(account) == 6:
        # pid
        return account + '@jiashu.com'
    return account

def app_1push(push_body, account):
    """
    app1次推送
    :param push_body:
    :param account:
    :return:
    """
    if account is None:
        logger.warn('push1account null')
        return

    account = handle_pid_account(account)

    try:
        push_params = redis_cal.send_cmd('get', ':'.join(('account', account)))
        if not push_params:
            logger.warn('push session not found: {0}'.format(account))
            return

        push_params = push_params.split(':')
        platform, ver = push_params[:2]
        push_func = find_push(platform, push_params[2])
        if not push_func:
            logger.warn('push_platform not found: %s' % platform)
            return

        logger.debug('push body: {0}, push_params: {1}'.format(push_body, push_params))
        push_func(push_body, push_params[2:])
    except Exception as ex:
        logger.error('push err: {0}'.format(ex), exc_info=True)


def handle_msg(packet):
    """
    account为空时，推送给所有人
    :param packet:
    :return:
    """
    logger.debug('cloud push packet: {0}'.format(packet))
    packet.pop('cancel', None)
    single_account = packet.pop('account', None)
    push_body = packet.pop('p', None)
    channel = packet.pop('ch', None)

    logger.debug('cloud push single_account: {0}, push_body: {1}, channel: {2}'.format(single_account, push_body, channel))
    if channel is None:
        return
    #批量，app
    p_batch, p_app = span_bits(channel, 1, 0, 0)

    if single_account is not None:
        if p_batch:
            logger.warn('cloud_push handle_msg:: not support batch push!!!')
        #单用户，意味着仅一种推送通道，dict对象键值不会受干扰
        #没有必要deepcopy
        if p_app:
            app_1push(push_body, single_account)
        return

    pid = push_body.get('id')
    primary_account, sub_accounts = dev_filter.send_multi_cmd(
        *combine_redis_cmds(test_primary_bound(pid), list_dev_subaccounts(pid)))
    if not primary_account:
        logger.warn('{0} not bound, no push'.format(pid))
        return

    logger.debug('primary account: {0}'.format(primary_account))
    primary_account = primary_account.split(':')[-1]
    sub_accounts.add(primary_account)
    logger.debug('cloud handle_msg sub_accounts: {0}, primary_account: {1}, pid: {2}'.format(sub_accounts, primary_account, pid))
    if p_batch:
        logger.warn('cloud_push handle_msg:: not support batch push!!!')
    if p_app:
        [app_1push(deepcopy(push_body), x) for x in sub_accounts]
