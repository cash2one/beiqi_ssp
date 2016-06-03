#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/12

@author: Jay
"""
import json
from util.convert import bs2utf8

def mk_share_file(fn, ref, thumb_fn, thumb_ref):
    file_dic = {fn: ref} if not thumb_fn else {fn: ref, thumb_fn: thumb_ref}
    file_u8 = dict([(bs2utf8(k), bs2utf8(v)) for k, v in file_dic.items()])
    return json.dumps(file_u8)
