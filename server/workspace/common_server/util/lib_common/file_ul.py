#coding:utf-8
import time
import re
from binascii import b2a_hex
from util.log_util import gen_log
from util.mq_packs.pt30_forward_pack import pack as forward_pack
from util.mq_packs.uni_pack import shortcut_mq
from util.sso.redis_cal import incre_unique_sn
from util.filetoken import extract_tk
from util.convert import bs2utf8, is_num, combine_redis_cmds, is_email
from util.filetoken import extract_ref, gen_file_tk
from util.crypto_rc4 import encrypt as rc4_encrypt, decrypt as rc4_decrypt


APP_VALID_SOURCE = (1, 2, 3)
USAGE_PATTERN = re.compile(r'^[_a-z\d]+$')
BY_CIPHER_KEY = '4c040405f78a48099900ef87c801244f'


def common_file_token(dev_filter, cur_account, fn, mode, ref):
    """
    获取文件上传/下载token，用于file模块认证（时效）
    :param dev_filter: redis object
    :param cur_account: 当前用户
    :param pid: 设备id
    :param fn: 上传/下载文件名
    :param share: 是否共享
    :param mode: 模式，0：上传；1：下载
    :param ref: 上传凭据
    """
    if not cur_account or not is_num(mode):
        return

    ul = int(mode) == 0
    # share = int(share)

    # if share:
    #     primary_account, is_sa = dev_filter.send_multi_cmd(
    #         *combine_redis_cmds(
    #             test_primary_bound(pid),
    #             is_dev_subaccounted(pid, cur_account)
    #         )
    #     )
    #     #主帐号必须有
    #     if primary_account:
    #         primary_account = primary_account.split(':')[-1]
    #         if not (primary_account == cur_account or is_sa):
    #             gen_log.warn('{0} not pa even sa {1}'.format(pid, cur_account))
    #             return
    #     else:
    #         gen_log.warn('{0} not bound'.format(pid))
    #         return

    if not ul:
        #下载
        _ = extract_ref(ref)
        if not _:
            gen_log.warn('downloading, ref extract fail: {0}'.format(ref))
            return

        ref_share, ref_by_app, ref_unique_key, ref_fn = _
        if ref_fn != fn:
            gen_log.warn('downloading, fn {0} not match {1}'.format(ref_fn, fn))
            return
    else:
        ref_by_app = True
        # ref_share = share

    return {
        'tk': gen_file_tk(
            cur_account,
            fn,
            ul,
            ref_by_app
            # ref_share
        ),
        'by': rc4_encrypt(cur_account, BY_CIPHER_KEY),
    }


def ul_args_ok(redis_cal, tk, src, usage):
    """
    确认参数
    :param redis_cal: redis计算对象
    :param tk:
    :param src:
    :param usage:
    :return:
    """
    tk_params = extract_tk(tk, True)
    if not tk_params:
        gen_log.warn('extract token fail')
        return None
    file_type = bs2utf8(src)
    if not is_num(file_type):
        gen_log.warn('src type invalid: {0}'.format(file_type))
        return None
    file_type = int(file_type)
    if file_type not in APP_VALID_SOURCE:
        gen_log.warn('src unknown: {0}'.format(file_type))
        return None

    share, by_app, pid, fn = tk_params
    unique_sn = 0
    if 0b100 == file_type:
    # 手机到手表，双向语音
        if not USAGE_PATTERN.search(usage):
            return None
        unique_sn = redis_cal.send_cmd(*incre_unique_sn())
        #忽略app的fn参数，重新设置
        fn = '_'.join(('bi', '%x' % unique_sn))

    #重新创建tk_params
    return (share, by_app, pid, fn), file_type, usage, unique_sn


def bi_directional_dispatch(mq_hub, unique_token, tk_params, file_source, usage, leveldb_fn, account):
    """
    执行双向文件分发
    :param mq_hub: redis对象
    :param tk_params:
    :param unique_token: 全局唯一序号
    :param file_source:
    :param usage:
    :param leveldb_fn:
    :param account: 当前用户帐号
    """
    if 0b100 != file_source:
        return
    if not account:
        return
    account = rc4_decrypt(account, BY_CIPHER_KEY)
    if not is_email(account):
        return

    #是否共享，是否由app上传，二进制id，原始文件名（非leveldb）
    share, by_app, pid, fn = tk_params

    mq_hub.send_cmd(
        *shortcut_mq(
            'spec_pt30',
            forward_pack(
                #分发双向二进制文件
                'dispatch_bi_dir_bin',
                #设备id如何处理
                b2a_hex(pid),
                {
                    'acc': account,
                    #用途，便于app和设备区分；信息流中作为cmd出现
                    'usage': usage,
                    #leveldb文件名
                    'leveldb_fn': leveldb_fn,
                    #产生时间
                    'ts': int(time.time()),
                    #声音文件初始文件名
                    'raw_fn': fn,
                    'unique_token': unique_token,
                }
            )
        )
    )
