#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-14

@author: Jay
"""
import hashlib

class SignatureChecker():

    @staticmethod
    def check(token, timestamp, nonce, signature):
        ls_data = [token, timestamp, nonce]
        sort_data = sorted(ls_data)
        str_data = "".join(sort_data)
        sha_data = hashlib.sha1(str_data).hexdigest()
        return sha_data == signature
