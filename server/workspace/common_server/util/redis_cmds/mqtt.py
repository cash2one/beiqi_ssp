#coding: utf8


MQTT_STATUS = 'mqtt_status'


def set_mqtt_status(account, status):
    return 'hset', MQTT_STATUS, account, status


def get_mqtt_status(account):
    return 'hget', MQTT_STATUS, account