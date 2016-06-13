#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/13

@author: Jay
"""
from tornado.testing import AsyncTestCase
from utest_lib.common import *
from utils.network.mqtt import MQTTClient
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET
from mqtt_server.common.opcode import *
from interfaces.mqtt_server.http_rpc import beiqi_msg_bcast


class MqttServerMsgBCastTest(AsyncTestCase):
    GMqttClient = MQTTClient()
    GMqttClient.init(MQTT_IP, 1883)
    GMqttClient.start()
    MqttServerMsgBCastTestHdl = None
    gid = random_str()
    payload = random_str()
    topic = C_SUB_BEIQI_MSG_BCAST.format(gid=gid)

    def test_mqtt_msg_bcast(self):
        self.MqttServerMsgBCastTestHdl = self

        self.GMqttClient.subscribe(self.topic, self.beiqi_msg_bcast_res)
        time.sleep(SYNC_WAIT_TIME)

        beiqi_msg_bcast(MQTT_SERVER_IP, gen_test_tk(), APP_SECRET, self.gid, self.payload)
        self.wait(timeout=SYNC_WAIT_TIME)

    def beiqi_msg_bcast_res(self, mqttc, userdata, topic, payload):
        self.assertTrue(topic == self.topic)
        self.assertTrue(payload == self.payload)
        self.MqttServerMsgBCastTestHdl.stop()