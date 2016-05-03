# coding=utf-8
"""
Created on 2015-4-23

@author: Jay
"""
import types


def require_login(func, *args, **kwargs):
    def _vatify_login(*args, **kwargs):
        request = args[0]
        session_id = request.get_secure_cookie('sid')
        if not isinstance(request._sessions_.get(session_id), types.StringType):
            request.redirect('/')
            return
        else:
            return func(*args, **kwargs)
    return _vatify_login