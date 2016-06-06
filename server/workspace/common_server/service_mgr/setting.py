# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""
from utils.service_control.finder import get_cur_ip

SERVICE_TYPE = "service_mgr"
VERSION = "0.0.1"

# MYSQL配置
DB_HOST = "192.168.2.192"
DB_PORT = 3306
DB_NAME = "service_mgr" + get_cur_ip().replace(".", "_")
DB_USER = "system"
DB_PWD = "System"

USED_SERVICES = [
    US_DEVICE_END,
    US_MAIL,
    US_SMS,
] = [
    "s_device_end",
    "s_mail",
    "s_sms"
]
