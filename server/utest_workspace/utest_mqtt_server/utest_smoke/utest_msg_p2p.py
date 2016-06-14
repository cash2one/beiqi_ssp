#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
from tornado.testing import AsyncTestCase
from utest_lib.common import *
from utils.network.mqtt import MQTTClient
from mqtt_server.common.opcode import *
from interfaces.mqtt_server.http_rpc import beiqi_msg_p2p


class MqttServerMsgP2PTest(AsyncTestCase):
    GMqttClient = MQTTClient()
    GMqttClient.init(MQTT_IP, 1883)
    GMqttClient.start()
    test_common_msg_p2p_hdl = None
    special_common_msg_p2p_hdl = None

    def test_mqtt_msg_p2p_common(self):
        self.test_common_msg_p2p_hdl = self

        sn = random_str()
        self.common_payload = random_str()
        self.common_topic = C_SUB_BEIQI_MSG_P2P.format(sn=sn)

        self.GMqttClient.subscribe(self.common_topic, self.comon_msg_p2p_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_p2p(MQTT_SERVER_IP, sn, self.common_payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def comon_msg_p2p_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self.common_topic)
        self.assertTrue(payload == self.common_payload)
        self.test_common_msg_p2p_hdl.stop()


    def test_mqtt_msg_p2p_special(self):
        self.special_common_msg_p2p_hdl = self

        sn = "PNZHANCHENJIN"
        self.special_payload = "1:play:audio:Sleep+Away.mp3:88d7dce4248c314fdd773f86b7198b31dd0aff81719dfd54aa033641df0a83b25cf5c6a1a146d340b0bbf3e2475dabefe4cbd1e8f4adeb706a91d6a02b28a80e57586dbfa413e19b29987f484660ec6709a94b74c2307ee1cb5e0f5d421cf0fdef08d10006197e47ce64eaeeafa8293e58a61d"
        self.special_topic = C_SUB_BEIQI_MSG_P2P.format(sn=sn)

        self.GMqttClient.subscribe(self.special_topic, self.special_msg_p2p_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_p2p(MQTT_SERVER_IP, sn, self.special_payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def special_msg_p2p_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self.special_topic)
        self.assertTrue(payload == self.special_payload)
        self.special_common_msg_p2p_hdl.stop()