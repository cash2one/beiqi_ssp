# coding=utf-8
"""
Created on 2015-4-23

@author: Jay
"""
from utils.service_control.setting import is_tp_service
from service_mgr.lib.service_group import ServiceGrpMgr
from service_mgr.setting import SERVICE_TYPE as SERVICE_MGR

# [关闭, 正在开启, 已经开启, 关闭中]
[CLOSED, OPENING, OPEN, CLOSING] = xrange(4)

menu = [{"name": '通用', 'url': '/common'},
        {'name': '服务管理', 'url': '/service_manager'}]

service_manager = [{'name': '所有逻辑服务', 'url': '/view_all_service'},
                   {'name': '第三方服务', 'url': '/view_tp_service'}]
service_manager.extend([{'name': service, 'url': '/view_logic_service?service=%s' % service}
                        for service in ServiceGrpMgr().get_service_grps()
                        if service != SERVICE_MGR and is_tp_service(service)])


common_manager = [{'name': '微信', 'url': '/view_wechat'},
                  {'name': '硬件类型', 'url': '/view_device_type'}]