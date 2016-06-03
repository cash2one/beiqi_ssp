#coding:utf8
import paho.mqtt.client as mqtt
from utils import logger

class MQTTCallback(object):
    """
    MQTT 回调处理
    """
    def __init__(self):
        pass

    def on_connect(self, mqttc, userdata, flags, rc):
        """
        连接mqtt服务器成功通知
        :param mqttc:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        logger.debug('mqtt onconnect!!')

    def on_disconnect(self, mqttc, userdata, rc):
        """
        断开mqtt服务器连接通知
        :param mqttc:
        :param userdata:
        :param rc:
        :return:
        """
        logger.debug('mqtt ondisconnect!!')

    def on_message(self, mqttc, userdata, msg):
        """
        接收到mqtt服务器消息通知
        :param mqttc:
        :param userdata:
        :param msg:
        :return:
        """
        pass


    def on_publish(self, mqttc, userdata, mid):
        """
        消息成功发布到mqtt服务器通知
        :param mqttc:
        :param userdata:
        :param mid:
        :return:
        """
        logger.debug('mqtt onpublish!!!, mqttc={0}, userdata={1}, mid={2}'.format(mqttc, userdata, mid))

    def on_subscribe(self, mqttc, userdata, mid, granted_qos):
        """
        成功从mqtt服务器预定消息通知
        :param mqttc:
        :param userdata:
        :param mid:
        :param granted_qos:
        :return:
        """
        pass

    def on_log(self, mqttc, userdata, level, string):
        """
        日志通知
        :param mqttc:
        :param userdata:
        :param level:
        :param string:
        :return:
        """
        pass


class MQTTClient(MQTTCallback):
    """
    MQTT客户端
    """
    def __init__(self, clientid=None):
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect

        super(MQTTClient, self).__init__()

    def init(self, host, port=1883):
        """
        mqtt初始化
        :param host: 主机
        :param port: 端口
        :return:
        """
        self.host = host
        self.port = port
        self._mqttc.connect(host, port, 60)
        logger.debug("mqtt clientid={0}".format(self._mqttc._client_id))


    def start(self):
        """
        服务开启
        :return:
        """
        self._mqttc.loop_forever()

    def stop(self):
        """
        服务停止
        :return:
        """
        self._mqttc.disconnect()

    def username_pw_set(self, username, password=None):
        """
        设置用户名和密码
        :param username:
        :param password:
        :return:
        """
        self._mqttc.username_pw_set(username, password)

    def user_data_set(self, userdata):
        """
        设置用户数据
        :param userdata:
        :return:
        """
        self._mqttc.user_data_set(userdata)

    def publish(self, topic, payload, qos=2, retain=False):
        """
        消息发布
        :param topic: 主题
        :param payload: 内容
        :param qos: qos
        :param retain:
        :return:
        """
        rsz = self._mqttc.publish(topic, payload, qos, retain)
        logger.debug('mqtt publish!!!, topic={0}, payload={1}, rsz={2}'.format(topic, payload, rsz))

    def subscribe(self, topic, qos=2):
        """
        消息预定
        :param topic: 主题
        :param qos: qos
        :return:None
        """
        self._mqttc.subscribe(topic, qos)

    def unsubscribe(self, topic):
        """
        取消某个消息的预定
        :param topic: 主题
        :return:
        """
        self._mqttc.unsubscribe(topic)
