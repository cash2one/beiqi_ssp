#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-25

@author: Jay
"""
from utest_lib.common import *
from utils.network.mqtt import MQTTClient
import time


class MqttPublishSubscribeTest(unittest.TestCase):
    publish_client = MQTTClient()
    publish_client.init(MQTT_IP, MQTT_PORT)
    subscribe_client = MQTTClient()
    subscribe_client.init(MQTT_IP, MQTT_PORT)
    publish_client.start()
    subscribe_client.start()
    time.sleep(SYNC_WAIT_TIME)
    topic = random_str(10)
    msg = random_str(10)

    @unittest_adaptor()
    def test_publish_subscribe(self):
        self.subscribe_client.subscribe(self.topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(self.topic, self.msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttPublishSubscribeTest::handle_topic,", topic, payload
        self.assertTrue(mqttc == self.subscribe_client)
        self.assertTrue(userdata is None)
        self.assertTrue(payload == self.msg)


class MqttPublishSubscribeSelfTest(unittest.TestCase):
    client = MQTTClient()
    client.init(MQTT_IP, MQTT_PORT)
    client.start()
    time.sleep(SYNC_WAIT_TIME)
    topic = random_str(10)
    msg = random_str(10)

    @unittest_adaptor()
    def test_publish_subscribe(self):
        self.client.subscribe(self.topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.client.publish(self.topic, self.msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttPublishSubscribeSelf::handle_topic,",topic, payload
        self.assertTrue(mqttc == self.client)
        self.assertTrue(userdata is None)
        self.assertTrue(payload == self.msg)


class MqttPublishSubscribeUserDataTest(unittest.TestCase):
    publish_client = MQTTClient()
    publish_client.init(MQTT_IP, MQTT_PORT)
    subscribe_client = MQTTClient()
    subscribe_client.init(MQTT_IP, MQTT_PORT)
    publish_user_data = "publish_data"
    subscribe_user_data = "subscribe_data"
    publish_client.user_data_set(publish_user_data)
    subscribe_client.user_data_set(subscribe_user_data)
    publish_client.start()
    subscribe_client.start()
    time.sleep(SYNC_WAIT_TIME)
    topic = random_str(10)
    msg = random_str(10)

    @unittest_adaptor()
    def test_publish_subscribe(self):
        self.subscribe_client.subscribe(self.topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(self.topic, self.msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttPublishSubscribeUserDataTest::handle_topic,",topic, payload
        self.assertTrue(mqttc == self.subscribe_client)
        self.assertTrue(userdata == self.subscribe_user_data)
        self.assertTrue(payload == self.msg)

class MqttWildcardSubscriptionsTest(unittest.TestCase):
    publish_client = MQTTClient()
    publish_client.init(MQTT_IP, MQTT_PORT)
    subscribe_client = MQTTClient()
    subscribe_client.init(MQTT_IP, MQTT_PORT)
    publish_client.start()
    subscribe_client.start()
    time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttWildcardSubscriptionsTest::handle_topic,",topic, payload
        pass

    @unittest_adaptor()
    def test_subscribe_separate_names(self):
        topic = "%s/%s" % (random_str(10), random_str(10))
        self.subscribe_client.subscribe(topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        msg = "separate_names"
        self.publish_client.publish(topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    @unittest_adaptor()
    def test_subscribe_match_any_name(self):
        field1 = random_str(10)
        field2 = random_str(10)
        field3 = random_str(10)

        pub_topic = "%s/%s/%s" % (field1, field2,field3)
        sub_topic1 = "%s/+/%s" % (field1, field3)
        msg = "match_any_name_middle"
        self.subscribe_client.subscribe(sub_topic1, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(pub_topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

        subscribe_client2 = MQTTClient()
        subscribe_client2.init(MQTT_IP, MQTT_PORT)
        subscribe_client2.start()
        time.sleep(SYNC_WAIT_TIME)

        sub_topic2 = "%s/%s/+" % (field1, field2)
        msg = "match_any_name_right"
        subscribe_client2.subscribe(sub_topic2, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(pub_topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

        subscribe_client3 = MQTTClient()
        subscribe_client3.init(MQTT_IP, MQTT_PORT)
        subscribe_client3.start()
        time.sleep(SYNC_WAIT_TIME)

        sub_topic3 = "+/%s/%s" % (field2, field3)
        msg = "match_any_name_left"
        subscribe_client3.subscribe(sub_topic3, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(pub_topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    @unittest_adaptor()
    def test_subscribe_recursively_match_names(self):
        field1 = random_str(10)
        field2 = random_str(10)
        field3 = random_str(10)

        pub_topic = "%s/%s/%s" % (field1, field2,field3)
        sub_topic1 = "%s/#" % (field1)
        msg = "recursively_match_names_one"
        self.subscribe_client.subscribe(sub_topic1, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(pub_topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

        subscribe_client2 = MQTTClient()
        subscribe_client2.init(MQTT_IP, MQTT_PORT)
        subscribe_client2.start()
        time.sleep(SYNC_WAIT_TIME)

        sub_topic2 = "%s/%s/#" % (field1, field2)
        msg = "recursively_match_names__two"
        subscribe_client2.subscribe(sub_topic2, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(pub_topic, msg, 2)
        time.sleep(SYNC_WAIT_TIME)

class MqttPublishSubscribeSelf(unittest.TestCase):
    client = MQTTClient()
    client.init(MQTT_IP, MQTT_PORT)
    client.start()
    time.sleep(SYNC_WAIT_TIME)
    topic = random_str(10)
    msg = random_str(10)

    @unittest_adaptor()
    def test_publish_subscribe_self(self):
        self.client.subscribe(self.topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.client.publish(self.topic, self.msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttPublishSubscribeSelf::handle_topic,",topic, payload
        self.assertTrue(mqttc == self.client)
        self.assertTrue(userdata is None)
        self.assertTrue(payload == self.msg)


class MqttPublishSubscribeJIDTopic(unittest.TestCase):
    publish_client = MQTTClient()
    publish_client.init(MQTT_IP, MQTT_PORT)
    subscribe_client = MQTTClient()
    subscribe_client.init(MQTT_IP, MQTT_PORT)
    publish_client.start()
    subscribe_client.start()
    time.sleep(SYNC_WAIT_TIME)
    topic = "xmpp_message/bridge"
    msg = random_str(10)

    @unittest_adaptor()
    def test_publish_subscribe_jid_topic(self):
        self.subscribe_client.subscribe(self.topic, self.handle_topic, 2)
        time.sleep(SYNC_WAIT_TIME)
        self.publish_client.publish(self.topic, self.msg, 2)
        time.sleep(SYNC_WAIT_TIME)

    def handle_topic(self, mqttc, userdata, topic, payload):
        print "MqttPublishSubscribeJIDTopic::handle_topic,",topic, payload
        self.assertTrue(mqttc == self.subscribe_client)
        self.assertTrue(userdata is None)
        self.assertTrue(payload == self.msg)
