#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-29

@author: Jay
"""
from utils import logger
from util.convert import is_num
from util.filetoken import check_tk_ref, gen_lvl_fn
from util.internal_forward.leveldb_encode import resolve_expire, DEV_APP


def down_parse(tk, r, file_source):
    tk_ref_params = check_tk_ref(tk, False, r)
    if not tk_ref_params:
        logger.warn('down_parse:: not tk_ref_params: {0}'.format(tk_ref_params))
        return

    if not is_num(file_source):
        logger.warn('file_src type invalid: {0}'.format(file_source))
        return

    file_source = int(file_source)
    if file_source > DEV_APP:
        logger.warn('file_src type invalid: {0}'.format(file_source))
        return
    return resolve_expire(file_source), gen_lvl_fn(*tk_ref_params)