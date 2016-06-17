#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/18

@author: Jay
"""
from utest_lib.common import *
from util.filetoken import *


class UtilFileTokenTest(unittest.TestCase):

    @unittest_adaptor()
    def test_file_tk(self):
        ref = gen_ref(True, True, 'c2000018122222'*10, 'abcde'*10)
        print "ref,",ref, len(ref)
        print "extract_ref,",extract_ref(ref)

        tk = gen_file_tk('c2000018', 'abcde', True, True)
        print "tk,",tk
        print "extract_tk,",extract_tk(tk, True)
        print "check_tk_ref,",check_tk_ref(tk, True, ref)

        print "gen_lvl_fn,",gen_lvl_fn(1, True, 'c2000018', 'abcde')

        share, by_app, account, fn = True, True, 'c2000018122222@beiqi.com', 'pnxhsndfef112.amr'
        sref = gen_ref(share, by_app, account, fn)
        print "sref,",sref, len(sref)
        share1, by_app1, account1, fn1 = extract_ref(sref)
        assert share == share1
        assert by_app == by_app1
        assert account == account1
        assert fn == fn1
        print "extract_short_ref,",share1, by_app1, account1, fn1


        stk = gen_file_tk('c2000018', 'abcde', True, True)
        sref = gen_ref(True, True, 'c2000018', 'abcde')
        print "stk,",stk
        print "extract_s_tk,",extract_tk(stk, True)
        print "check_s_tk_ref,",check_tk_ref(stk, True, sref)
    @unittest_adaptor()
    def test_file_tk1(self):
        tk = "4BBQMDgxMTAxNTM1MDAwMDEzV0+uA1JFQzAwODYuV0FW"
        print extract_tk(tk, True)

        print "1"

    @unittest_adaptor()
    def test_gen_lvl_fn(self):
        share = "1"
        by_app = "0"
        acc = "acc"
        fn = "test.fn"
        print gen_lvl_fn(share, by_app, acc, fn)