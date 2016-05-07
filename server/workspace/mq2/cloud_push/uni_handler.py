#coding:utf8

import json
from tornado.gen import coroutine

from utils import logger
from util.sso.dev_active import *
from util.redis.redis_client import Redis
from util.stream_config_client import load as conf_load
from util.convert import combine_redis_cmds, parse_ip_port
from util.bit import span_bits
from util.internal_forward.gen_internal_client import GeneralInternalClient
from util.internal_forward.batch_push_encode import encode as batch_push_encode
from . import find_push
from util.oem_conv import get_mb_key, parse_oem_options, oem_accounts
from copy import deepcopy


group = dict(conf_load('redis.ini', 'push_svr.ini'))
redis_conf = group.get('redis.ini')
batch_push_conf = group.get('push_svr.ini')

redis_cal = Redis(redis_conf.get('calculation', 'url'))
dev_filter = Redis(redis_conf.get('dev_filter', 'url'))
account_cache = Redis(redis_conf.get('oauth', 'url'))
batch_push_client = GeneralInternalClient(parse_ip_port(batch_push_conf.get('default', 'mq_host')))


def handle_pid_account(account):
    if len(account) == 6:
        # pid
        return account + '@jiashu.com'
    return account

@coroutine
def forward_batch(push_body, key_acc, rel_accounts):
    """
    转发批量推送
    :param push_body:
    :param key_acc: 相关帐号，用于查询akey，一个就够
    :param rel_accounts: 所有帐号列表
    :return:
    """
    #通过用户帐号查找api_key
    _ = account_cache.send_cmd(*get_mb_key(key_acc))
    if not _:
        #不存在key
        return
    mobile, api_key = _.split(':')
    oem_ob = oem_accounts.get(api_key)
    if not oem_ob:
        #非oem帐号
        return
    _ = parse_oem_options(oem_ob.get('opt_mask') or api_key)
    if not _:
        return
    if not _[1]:
        #不批量推送
        return

    token = push_body.get('cb')
    if token:
        token = token.split(':')[-1]
        src_account = dev_filter.send_cmd(*get_dev_sms_src(token))
    else:
        src_account = None

    #需要批量发送
    push_body.update(
        {
            'accs': [x.split('@')[0] for x in rel_accounts if x]
            if rel_accounts else (key_acc.split('@')[0],),
            'src_acc': src_account.split('@')[0] if src_account else '',
        }
    )
    pid = push_body.get('id')
    imsi = dev_filter.send_cmd(*get_dev_imeiimsi_etc(pid))
    imsi = imsi.split(':')[-2] if imsi else ''
    push_body.update({'imsi': imsi})

    result = yield batch_push_client.forward(
        batch_push_encode(
            api_key,
            pid,
            json.dumps(push_body, separators=(',', ':'))
        )
    )
    logger.debug('batch push: %s' % result)


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
            forward_batch(deepcopy(push_body), single_account, None)
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
        forward_batch(deepcopy(push_body), primary_account, sub_accounts)
    if p_app:
        [app_1push(deepcopy(push_body), x) for x in sub_accounts]
