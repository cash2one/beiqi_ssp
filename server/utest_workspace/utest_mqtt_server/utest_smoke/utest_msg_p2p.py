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
    MqttServerMsgP2PHdl = None
    sn = random_str()
    payload = random_str()
    topic = C_SUB_BEIQI_MSG_P2P.format(sn=sn)

    def test_mqtt_msg_p2p(self):
        self.MqttServerMsgP2PHdl = self

        self.GMqttClient.subscribe(self.topic, self.beiqi_msg_p2p_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_p2p(MQTT_SERVER_IP, self.sn, self.payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def beiqi_msg_p2p_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self.topic)
        self.assertTrue(payload == self.payload)
        self.MqttServerMsgP2PHdl.stop()