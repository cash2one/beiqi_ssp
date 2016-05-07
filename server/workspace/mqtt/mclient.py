#coding: utf8
import time
from setproctitle import setproctitle
import paho.mqtt.client as mqtt
from utils import logger
from util.redis_cmds.mqtt import set_mqtt_status
from util.redis.redis_client import Redis
from setting import DEV_RDS_URI


logger.init_log('mclient', 'mclient')
setproctitle('mclient')


dev_filter = Redis(DEV_RDS_URI)

host = '127.0.0.1'

online_topic = 'node/online/+'
offline_topic = 'node/offline/+'


def on_connect(client, userdata, flags, rc):
    # client.publish(online_topic)
    client.subscribe(offline_topic)
    client.subscribe(online_topic)


def on_message(client, userdata, msg):
    topic = msg.topic
    topic, acc = topic.rsplit('/', 1)
    payload = msg.payload
    logger.debug('topic = %r, acc = %r, payload = %r', topic, acc, payload)
    if topic == 'node/online':
        status = 'online'
    elif topic == 'node/offline':
        status = 'offline'

    status = status + ':' + str(time.time())
    dev_filter.send_cmd(*set_mqtt_status(acc, status))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.debug('disconnected')


client = mqtt.Client(client_id='sub_client')
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(host, 1883, 60)
client.loop_forever()
