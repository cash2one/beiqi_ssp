#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/14

@author: Jay
"""
from utest_lib.common import *
from tornado.testing import AsyncTestCase
from utils.network.mqtt import MQTTClient
from interfaces.api_server.http_rpc import chat_bcast
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET
from mqtt_server.common.opcode import C_SUB_BEIQI_MSG_BCAST


class APIChatMsgBcastTest(AsyncTestCase):
    GMqttClient = MQTTClient()
    GMqttClient.init(MQTT_IP, 1883)
    GMqttClient.start()

    test_chat_msg_bcast_hdl = None

    def test_chat_msg_bcast(self):
        self.test_chat_msg_bcast_hdl = self

        file_type = "3"
        fn = "test_fn.amr"
        ref = "reftest" * 20

        self.bcast_topic = C_SUB_BEIQI_MSG_BCAST.replace("{gid}", "#")
        print self.bcast_topic
        self.GMqttClient.subscribe(self.bcast_topic, self.chat_bcast_res)
        time.sleep(SYNC_WAIT_TIME)

        chat_bcast(SERVER_IP, gen_test_tk(), APP_SECRET, file_type, fn, ref)
        self.wait(timeout=SYNC_WAIT_TIME)

    def chat_bcast_res(self, mqttc, userdata, topic, payload):
        print topic
        self.test_chat_msg_bcast_hdl.stop()

