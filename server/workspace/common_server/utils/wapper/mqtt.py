#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-27

@author: Jay
"""
import ujson
from utils.crypto import XXTEACrypto
from utils import logger

def mqtt_subscribe_decorator(mqtt_client_obj, topic):
    def mqtt_fun_subscriber(handler_fun):
        mqtt_client_obj.subscribe(topic, handler_fun)
        logger.info("MQTT:subscribe topic:%s, handler_fun:%s" % (topic, handler_fun))
        return handler_fun
    return mqtt_fun_subscriber



def mqtt_publish_decorator(use_json_dumps=False, xxtea_key=None, mqtt_sign=None):
    def mqtt_publish_func_decorator(fun):
        def mqtt_publish_param_decorator(self, topic, payload=None, *args, **kwargs):
            logger.info("MQTT:publish topic:%s, payload:%s" % (topic, payload))
            payload.__setitem__('sign', mqtt_sign) if mqtt_sign else None
            payload = ujson.dumps(payload) \
                if use_json_dumps and payload is not None\
                else payload
            payload = XXTEACrypto.instance(xxtea_key).encrypt(payload) \
                if xxtea_key and payload is not None\
                else payload
            return fun(self, topic, payload, *args, **kwargs)
        return mqtt_publish_param_decorator
    return mqtt_publish_func_decorator



def mqtt_onmessage_decorator(use_json_loads=False, xxtea_key=None):
    def mqtt_onmessage_func_decorator(fun):
        def mqtt_onmessage_param_decorator(self, mqttc, userdata, msg):
            try:
                msg.payload = XXTEACrypto.instance(xxtea_key).decrypt(msg.payload) \
                    if xxtea_key and msg.payload\
                    else msg.payload
                msg.payload = ujson.loads(msg.payload) \
                    if use_json_loads and msg.payload \
                    else msg.payload
            except:
                logger.warn("mqtt_onmessage_decorator Error!!! topic:%s payload:%s" % (msg.topic, msg.payload))
                return
            return fun(self, mqttc, userdata, msg)
        return mqtt_onmessage_param_decorator
    return mqtt_onmessage_func_decorator