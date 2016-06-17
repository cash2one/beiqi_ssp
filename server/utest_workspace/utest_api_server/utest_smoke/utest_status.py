#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2016/6/16

@author: Jay
"""
from utest_lib.common import *
from interfaces.api_server.http_rpc import get_status
from interfaces.mqtt_server.mqtt import c_pub_offline_req, c_pub_online_req
from utils.network.mqtt import MQTTClient
from utest_lib import gen_test_tk
from util.oem_account_key import APP_SECRET


mqtt_client = MQTTClient()
mqtt_client.init(MQTT_IP, MQTT_PORT)
mqtt_client.start()


def check_status(user_list, status):
    get_status_res = get_status(SERVER_IP, gen_test_tk(), APP_SECRET, user_list)
    for k , v in get_status_res.items():
        if k not in user_list:
            return False
        if v.split(":")[0] != status:
            return False
    return True


class MqttServerStatusTest(unittest.TestCase):
    def test_mqtt_status(self):
        test_count = 3
        user_list = [TEST_SN]

        for i in xrange(test_count):
            c_pub_online_req(mqtt_client, TEST_SN)
            time.sleep(SYNC_WAIT_TIME)
            self.assertTrue(check_status(user_list, "online"))
            c_pub_offline_req(mqtt_client, TEST_SN)
            self.assertTrue(check_status(user_list, "offline"))