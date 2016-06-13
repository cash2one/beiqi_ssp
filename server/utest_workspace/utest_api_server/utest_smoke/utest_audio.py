#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/5/10

@author: Jay
"""
from utest_lib.common import *
from utils.network.mqtt import MQTTClient
from tornado.testing import AsyncTestCase
from interfaces.api_server.http_rpc import get_cls, get_album, get_rdm_list, pub_2_dev
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


PUB_BEIQI_MSG_P2P = "BEIQI_MSG_P2P/{sn}"
SUB_BEIQI_MSG_P2P = "BEIQI_MSG_P2P/#"


APIAudioSend2DevTestHdl = None

class MqttInst(MQTTClient):
    def on_message(self, mqttc, userdata, msg):
        if APIAudioSend2DevTestHdl:
            APIAudioSend2DevTestHdl.stop()

GMqttClient = MqttInst()
GMqttClient.init(MQTT_IP, 1883)
GMqttClient.subscribe(SUB_BEIQI_MSG_P2P, None)
GMqttClient.start()


class APIAudioAudioClsTest(unittest.TestCase):
    def test_audio_list(self):
        self.assertTrue(get_cls(SERVER_IP, gen_test_tk(), APP_SECRET))


class APIAudioAudioAlbumTest(unittest.TestCase):
    def test_audio_list(self):
        cls_ls = get_cls(SERVER_IP, gen_test_tk(), APP_SECRET)
        select_cls = random.choice(cls_ls)
        print "select_cls,",select_cls
        self.assertTrue(get_album(SERVER_IP, gen_test_tk(), APP_SECRET, select_cls['id']))


class APIAudioAudioListTest(unittest.TestCase):
    def test_audio_list(self):
        self.assertTrue(get_rdm_list(SERVER_IP, gen_test_tk(), APP_SECRET))


class APIAudioSend2DevTest(AsyncTestCase):
    def test_pub_2_dev(self):
        audio_ls = get_rdm_list(SERVER_IP, gen_test_tk(), APP_SECRET)
        print audio_ls
        select_audio = random.choice(audio_ls)

        sn ="PNZHANCHENJIN"
        pub_2_dev(SERVER_IP, gen_test_tk(), APP_SECRET, sn, select_audio['name'], select_audio['ref'])

        global APIAudioSend2DevTestHdl
        APIAudioSend2DevTestHdl = self
        self.wait(timeout=5)

