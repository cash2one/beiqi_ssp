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
from mqtt_server.common.opcode import C_SUB_BEIQI_MSG_P2P


APIAudioSend2DevTestHdl = None


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
    GMqttClient = MQTTClient()
    GMqttClient.init(MQTT_IP, 1883)
    GMqttClient.start()

    test_pub_2_dev_hdl = None

    def test_pub_2_dev(self):
        self.test_pub_2_dev_hdl = self

        audio_ls = get_rdm_list(SERVER_IP, gen_test_tk(), APP_SECRET)
        print audio_ls
        select_audio = random.choice(audio_ls)
        sn ="PNZHANCHENJIN"

        self.p2d_topic = C_SUB_BEIQI_MSG_P2P.format(sn = sn)
        self.GMqttClient.subscribe(self.p2d_topic, self.pub_2_dev_res)
        time.sleep(SYNC_WAIT_TIME)

        pub_2_dev(SERVER_IP, gen_test_tk(), APP_SECRET, sn, select_audio['name'], select_audio['ref'])
        self.wait(timeout=5)

    def pub_2_dev_res(self, mqttc, userdata, topic, payload):
        print "pub_2_dev_res,",payload
        self.assertTrue(topic == self.p2d_topic)

        self.test_pub_2_dev_hdl.stop()




