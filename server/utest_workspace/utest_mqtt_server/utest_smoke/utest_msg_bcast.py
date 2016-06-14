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
from interfaces.mqtt_server.http_rpc import beiqi_msg_bcast


class MqttServerMsgBCastTest(AsyncTestCase):
    GMqttClient = MQTTClient()
    GMqttClient.init(MQTT_IP, 1883)
    GMqttClient.start()
    test_common_gid_payload_hdl = None
    test_special_gid_payload_hdl = None
    gid = random_str()
    payload = random_str()
    topic = C_SUB_BEIQI_MSG_BCAST.format(gid=gid)

    def test_mqtt_msg_bcast_common(self):
        self.test_common_gid_payload_hdl = self

        self.GMqttClient.subscribe(self.topic, self.beiqi_msg_bcast_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_bcast(MQTT_SERVER_IP, self.gid, self.payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def beiqi_msg_bcast_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self.topic)
        self.assertTrue(payload == self.payload)
        self.test_common_gid_payload_hdl.stop()


    def test_special_gid_payload(self):
        gid = 775817
        self.sgp_payload = "18610060484%40jiashu.com:3:test_fn.amr:reftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftestreftest:::"

        self._sgp_topic = C_SUB_BEIQI_MSG_BCAST.format(gid=gid)
        self.test_special_gid_payload_hdl = self

        self.GMqttClient.subscribe(self._sgp_topic, self.special_gid_payload_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_bcast(MQTT_SERVER_IP, gid, self.sgp_payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def special_gid_payload_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self._sgp_topic)
        self.assertTrue(payload == self.sgp_payload)
        self.test_special_gid_payload_hdl.stop()