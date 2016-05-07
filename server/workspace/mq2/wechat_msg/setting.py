#coding:utf-8

MQTT_HOST = "localhost"
MQTT_PORT = 1883

PUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/{0}"
SUB_BEIQI_MSG_BCAST = "BEIQI_MSG_BCAST/#"

WECHAT_UPLOAD_URL = 'http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s'
WECHAT_CUSTOMER_SERVICE_URL = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'

SSP_DOWNLOAD_FILE_URL = 'http://api.beiqicloud.com:8106/down?tk=%s&r=%s'