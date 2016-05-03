#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-13

@author: Jay
"""
from utils.crypto.sign import Signer
from utils import error_code
from utils import logger
from utils.crypto import UrlCrypto, XXTEACrypto
from utils.service_control.parser import ArgumentParser
from utils.service_control.finder import get_cur_ip
from utils.service_control.setting import SM_TCP_PORT

def sign_checker(sign_params=None):
    def sign_fun_checker(fun):
        def sign_param_checker(self, *args, **kwargs):
            if "sign" not in kwargs:
                logger.error("%s:%s ERROR_SIGN_ERROR, not sign param!!!" % (self.__class__.__name__, fun.__name__))
                return {"result": error_code.ERROR_SIGN_ERROR}

            sign = kwargs.pop('sign')
            if not (Signer().check_sign(sign, sign_params) if sign_params else Signer().check_sign(sign, **kwargs)):
                logger.error("%s:%s ERROR_SIGN_ERROR, check_sign false!!!" % (self.__class__.__name__, fun.__name__))
                return {"result": error_code.ERROR_SIGN_ERROR}
            return fun(self, *args, **kwargs)
        return sign_param_checker
    return sign_fun_checker


def sm_sign_checker():
    def sm_sign_fun_checker(fun):
        def sm_sign_param_checker(self, *args, **kwargs):
            if "sign" not in kwargs:
                logger.error("%s:%s ERROR_SIGN_ERROR, not sign param!!!" % (self.__class__.__name__, fun.__name__))
                return {"result": error_code.ERROR_SIGN_ERROR}

            sign = kwargs.pop('sign')
            if not Signer().check_sign(sign, get_cur_ip(), SM_TCP_PORT):
                logger.error("%s:%s ERROR_SIGN_ERROR, check_sign false!!!" % (self.__class__.__name__, fun.__name__))
                return {"result": error_code.ERROR_SIGN_ERROR}
            return fun(self, *args, **kwargs)
        return sm_sign_param_checker
    return sm_sign_fun_checker


def crypto_adaptor(use_xxtea=False):
    def crypto_fun_adaptor(fun):
        def crypto_param_adaptor(self, *args, **kwargs):
            crypt = XXTEACrypto(ArgumentParser().args.xxtea_key) \
                if use_xxtea \
                else UrlCrypto()
            args = [crypt.decrypt(arg) for arg in args]
            kwargs = dict((k, crypt.decrypt(kwargs[k]) )for k, v in kwargs.items())

            body = crypt.decrypt(self.request.body)
            kwargs.update(dict(pair.split("=") for pair in body.split("&"))) if body else None

            result = fun(self, *args, **kwargs)
            ouput_result = crypt.encrypt(result)
            return ouput_result
        return crypto_param_adaptor
    return crypto_fun_adaptor