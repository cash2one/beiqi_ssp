#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-7

@author: Jay
"""
from utest_lib.common import *
from utils.service_control.processer import start_process, stop_process
from utils.service_control.caster import BEAT_INTERVAL
from utils.service_control.checker import HEARTBEAT_EXPIRE_TIME


cur_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
service_mgr_path = os.path.join(cur_file_path, "workspace", "common_server", "service_mgr", "start.py")

redis_params = " --redis_passwd %s" % REDIS_PASSWD if REDIS_PASSWD else ""
SERVICE_ARGS_DIC = {
    ST_PANDORA: "",
}

def start_service_mgr():
    args = "--db_host %s --db_port %s --db_user %s --db_password %s" % (MYSQL_IP, MYSQL_PORT, MYSQL_USER, MYSQL_PASS)
    start_process(service_mgr_path, args)

def stop_service_mgr():
    stop_process(service_mgr_path)

def restart_service_mgr():
    stop_service_mgr()
    start_service_mgr()

def start_logic_services():
    for service in SERVICE_TYPE:
        if service == ST_SERVICE_MGR:
            continue

        path = os.path.join(cur_file_path, "workspace", "_".join(service.split("_")[1:]), "start.py")
        start_process(path, args=SERVICE_ARGS_DIC[service])
        logger.warn("sleep %ss for %s heartbeat:%s!!!" % (BEAT_INTERVAL, service, path))
        time.sleep(BEAT_INTERVAL*2)

def stop_logic_services():
    for service in SERVICE_TYPE:
        if service == ST_SERVICE_MGR:
            continue

        path = os.path.join(cur_file_path, "workspace", "_".join(service.split("_")[1:]), "start.py")
        stop_process(path)
        logger.warn("sleep %ss for %s heartbeat:%s!!!" % (BEAT_INTERVAL, service, path))
        time.sleep(1)

def restart_logic_services():
    stop_logic_services()
    start_logic_services()


def restart_services():
    stop_services()
    start_services()

def start_services():
    start_service_mgr()
    sm_sleep_time = HEARTBEAT_EXPIRE_TIME + 10
    logger.warn("sleep %ss for service_mgr check dead service!!!" % sm_sleep_time)
    time.sleep(sm_sleep_time)
    start_logic_services()

def stop_services():
    stop_logic_services()
    stop_service_mgr()