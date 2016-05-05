#coding:utf-8


from util.id_conv import rawid_tuple
from util.convert import combine_redis_cmds, bs2utf8
from util.sso.dev_active import list_dev_subaccounts, test_primary_bound,\
    test_dev_exist, get_all_alias, is_dev_subaccounted, set_alias
from util.sso.account import get_mb_key, get_mobile
from utils import logger
from util.oem_account_key import oem_accounts
from itertools import izip
from util.redis.async_redis.redis_resp import decode_resp_ondemand


def dev_alias(dev_filter, pid, cur_account, alias):
    """
    设置别名
    :param dev_filter:
    :param pid:
    :param cur_account:
    :param alias:
    :return:
    """
    if not (isinstance(cur_account, str) and isinstance(alias, basestring)):
        return

    pid = rawid_tuple(pid, True)
    if not pid or len(alias) > 15 or ':' in alias:
        return

    alias = bs2utf8(alias)
    pid, typ, sn, io = pid
    #子帐号是否关注，主帐号拥有
    is_sub_fo, primary_account = dev_filter.send_multi_cmd(
        *combine_redis_cmds(
            is_dev_subaccounted(pid, cur_account),
            test_primary_bound(pid)
        )
    )

    if not primary_account:
        return
    _, _, primary_account = primary_account.split(':')
    if not (primary_account == cur_account or is_sub_fo):
        return
    dev_filter.send_cmd(*set_alias(pid, cur_account, alias))
    return True


def _member_account(dev_filter, account_cache, pid, cur, primary_account, sub_accounts, acc_alias_list):
    """
    :param cur: 当前帐号
    :param primary_account: 主帐号
    :param sub_accounts: 子帐号列表
    :param acc_alias_list: 帐号别名列表
    :return:
    """
    sub_accounts = tuple(sub_accounts)
    ls = dict(((ac, acc_alias_list.get(ac, '')) for ac in sub_accounts))
    ls.update({primary_account: acc_alias_list.get(primary_account, '')})

    return {
        'list': ls,
        'me': cur,
        'primary': primary_account,
        'mc': dict(((y, x) for x, y in find_all_contacts(dev_filter, account_cache, pid)))
    }


def dev_members(dev_filter, account_cache, pid, cur_account):
    """
    设备成员列表
    :param dev_filter:
    :param account_cache:
    :param pid:
    :param cur_account:
    :return:
    """
    primary, sub_accs, acc_alias_tuple = dev_filter.send_multi_cmd(
        *combine_redis_cmds(
            test_primary_bound(pid),
            list_dev_subaccounts(pid),
            get_all_alias(pid)
        )
    )
    if not primary:
        return None
    primary = primary.split(':')[-1]
    _ = _member_account(dev_filter, account_cache, pid, cur_account, primary, sub_accs, acc_alias_tuple)
    return _


def find_all_contacts(dev_filter, account_cache, pid):
    """
    查找pid相关的所有帐号
    :param pid:
    :param dev_filter:
    :param account_cache:
    :return:
    """
    primary_account, sub_accounts = dev_filter.send_multi_cmd(
        *combine_redis_cmds(test_primary_bound(pid), list_dev_subaccounts(pid)))
    if not primary_account:
        return

    primary_account = primary_account.split(':')[-1]
    sub_accounts = sub_accounts or set()
    sub_accounts.add(primary_account)

    #拥有/关注某设备的用户帐号必定属于同一api_key，因此只需要查询主帐号即可
    _ = account_cache.send_cmd(*get_mb_key(primary_account)) or None
    api_key = _.split(':')[-1] if _ else None
    oem_ob = oem_accounts.get(api_key)
    if oem_ob:
        api_key = oem_ob.get('opt_mask') or api_key

    sub_accounts = tuple(sub_accounts)
    #根据get_mobile函数的约定
    #sub_accounts参数为tuple，则mobiles返回值不管有无，均为tuple/list类型
    mobiles = get_mobile(account_cache, api_key, sub_accounts)
    if isinstance(mobiles, str):
        mobiles = (mobiles,)
    if len(mobiles) != len(sub_accounts):
        logger.warn('mobile neq sub_accs: {0}, {1}'.format(mobiles, sub_accounts))
        return
    for x in izip(mobiles, sub_accounts):
        yield x
