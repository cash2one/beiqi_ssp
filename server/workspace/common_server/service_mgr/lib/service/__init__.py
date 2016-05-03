#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-27

@author: Jay
"""

class ServiceComposeCtl(object):
    def __init__(self):
        self.cp_module_dic = {}

    def add_cp(self, cp_obj):
        self.cp_module_dic[cp_obj.name()] = cp_obj

    def start_cp(self):
        [cp.start() for cp in self.cp_module_dic.values()]

    def stop_cp(self):
        [cp.stop() for cp in self.cp_module_dic.values()]

    def find_cp(self, name):
        return self.cp_module_dic.get(name, None)


class IServiceCompose(object):

    @staticmethod
    def name():
        pass

    def start(self):
        pass

    def stop(self):
        pass


