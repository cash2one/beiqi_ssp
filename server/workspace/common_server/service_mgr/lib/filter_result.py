#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-11

@author: Jay
"""

class FilterResult(object):
    def __init__(self):
        self.service_data = None

    def form(self, *args, **kwargs):
        pass

    def _sort(self):
        pass

    def result(self):
        self._sort()
        return self.service_data

class FilterServiceDicNotKeyResult(FilterResult):
    def __init__(self):
        super(FilterServiceDicNotKeyResult, self).__init__()
        self.service_data = []

    def form(self, service_grp_id, ip, state, id_service_dic):
        service_dic_ls = [service_obj.get_info_dic() for service_obj in id_service_dic.values()]
        self.service_data.extend(service_dic_ls)

    def _sort(self):
        self.service_data.sort(key=lambda x: x['id'])


class FilterServiceObjNotKeyResult(FilterResult):
    def __init__(self):
        super(FilterServiceObjNotKeyResult, self).__init__()
        self.service_data = []

    def form(self, service_grp_id, ip, state, id_service_dic):
        self.service_data.extend(id_service_dic.values())

    def _sort(self):
        pass


class FilterServiceDicKeyGrpResult(FilterResult):
    def __init__(self):
        super(FilterServiceDicKeyGrpResult, self).__init__()
        self.service_data = {}

    def form(self, service_grp_id, ip, state, id_service_dic):
        service_dic_ls = [service_obj.get_info_dic() for service_obj in id_service_dic.values()]
        if service_dic_ls:
            self.service_data.setdefault(service_grp_id, []).extend(service_dic_ls)

    def _sort(self):
        [service_ls.sort(key=lambda x: x['id']) for service_ls in self.service_data.values()]

class FilterTPServiceNotKeyResult(FilterResult):
    def __init__(self):
        super(FilterTPServiceNotKeyResult, self).__init__()
        self.service_data = []

    def form(self, service_grp_id, service_dic_ls):
        self.service_data.extend(service_dic_ls)

    def _sort(self):
        self.service_data.sort(key=lambda x: x['id'])


class FilterTPServiceKeyGrpResult(FilterResult):
    def __init__(self):
        super(FilterTPServiceKeyGrpResult, self).__init__()
        self.service_data = {}

    def form(self, service_grp_id, service_dic_ls):
        self.service_data.setdefault(service_grp_id, []).extend(service_dic_ls)

    def _sort(self):
        [service_ls.sort(key=lambda x: x['id']) for service_ls in self.service_data.values()]