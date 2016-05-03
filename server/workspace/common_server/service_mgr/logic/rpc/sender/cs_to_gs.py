#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-28

@author: Jay
"""
import random
import ujson
from utils.network.tcp import TcpRpcClient
from utils.wapper.catch import except_adaptor
from utils.crypto.sign import Signer
from service_mgr.logic.rpc import TCP_SIGN

class GsRpcClient(TcpRpcClient):
    """
    连接gs的rpc client
    """
    def __init__(self, host, port):
        super(GsRpcClient, self).__init__(str(host), int(port))

    @except_adaptor()
    def clear_cache(self):
        params = {"sign": TCP_SIGN}
        return self.fetch_sync("clear_cache", ujson.dumps(params))

    @except_adaptor()
    def get_db_params(self):
        """
        获取服务的db参数
        :return:
        """
        params = {"sign": TCP_SIGN}
        return self.fetch_sync("get_db_params", ujson.dumps(params))

    @except_adaptor()
    def verify(self):
        """
        验证服务是否有效，随机一个参数给服务去签名，如果签名有效即服务有效
        :return:
        """
        factor = random.randint(1, 10000)
        params = {"sign": TCP_SIGN, "factor": factor}
        factor_sign = self.fetch_sync("verify", ujson.dumps(params))
        return Signer().check_sign(factor_sign, factor)

