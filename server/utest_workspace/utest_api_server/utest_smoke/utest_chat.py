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


PUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/{gid}"
SUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/#"


APIChatMsgBcastTestHdl = None

class MqttInst(MQTTClient):
    def on_message(self, mqttc, userdata, msg):
        if APIChatMsgBcastTestHdl:
            APIChatMsgBcastTestHdl.stop()

GMqttClient = MqttInst()
GMqttClient.init(MQTT_IP, 1883)
GMqttClient.subscribe(SUB_BEIQI_MSG_BCAST, None)
GMqttClient.start()

class APIChatMsgBcastTest(AsyncTestCase):
    def test_chat_msg_bcast(self):
        file_type = "3"
        fn = "test_fn.amr"
        ref = "reftest" * 20

        chat_bcast(SERVER_IP, gen_test_tk(), APP_SECRET, file_type, fn, ref)
        global APIChatMsgBcastTestHdl
        APIChatMsgBcastTestHdl = self
        self.wait(timeout=5)

