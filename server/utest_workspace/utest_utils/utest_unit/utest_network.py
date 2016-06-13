#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-4-29

@author: Jay
"""
from utest_lib.common import *
from utils.service_control.finder import IpFinder, get_random_port


class TestTcpRpcHandler(TcpRpcHandler):
    def add(self, para1, para2):
        return para1 + para2

class TCPRPCTest(unittest.TestCase):
    TEST_PORT = get_random_port()
    TcpRpcServer(TEST_PORT, TestTcpRpcHandler).start()
    tcp_rpc_client = TcpRpcClient(IpFinder().get_cache_inter_net_ip(), TEST_PORT)

    # 初始化工作
    def setUp(self):
        logger.init_log("TCPRPCTest", "TCPRPCTest")

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_tcp_rpc_ping(self):
        self.assertEqual(self.tcp_rpc_client.ping(), "ping response!")

    @unittest_adaptor()
    def test_tcp_rpc_add(self):
        para1 = 1
        para2 = 2
        self.assertTrue(self.tcp_rpc_client.fetch_async("add", para1, para2), para1 + para2)


@route(r'/add', name='add')
class AddHandle(HttpRpcHandler):
    @web_adaptor()
    def get(self, para1, para2):
        return para1+para2

    def post(self):
        return self.get()


class TestHttpRpcApp(HttpRpcServer):
    __metaclass__ = Singleton

    def __init__(self, port,):
        # register handlers
        super(TestHttpRpcApp, self).__init__(port, False)


class HTTPRPCTest(unittest.TestCase):
    TEST_HTTP_PORT = get_random_port()
    TestHttpRpcApp(TEST_HTTP_PORT).start()
    http_rpc_client = HttpRpcClient(IpFinder().get_cache_inter_net_ip(), TEST_HTTP_PORT)

    # 初始化工作
    def setUp(self):
        logger.init_log("HTTPRPCTest", "HTTPRPCTest")

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_http_rpc_ping(self):
        self.assertEqual(self.http_rpc_client.ping(), "ping response!")

    @unittest_adaptor()
    def test_http_rpc_add(self):
        para1 = 1
        para2 = 2
        url = "add?para1=%s&para2=%s" % (para1, para2)
        self.assertTrue(self.http_rpc_client.fetch_async(url), para1 + para2)

class UdpClientTest(unittest.TestCase):
    udp_port = get_random_port()
    UdpServer(udp_port).start()
    udp_client = UdpClient(IpFinder().get_cache_inter_net_ip(), udp_port)

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @unittest_adaptor()
    def test_udp_send_recv(self):
        body = ujson.dumps(random_str())
        self.udp_client.send_async(body)
        data,addr = self.udp_client.socket.recvfrom(1024)
        self.assertTrue(data == body)