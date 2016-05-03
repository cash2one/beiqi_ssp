#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-6-2

@author: Jay
"""
import argparse
from utils.logger import INFO
from utils.meta.singleton import Singleton
from finder import get_cur_ip


def parser_boolean(b):
    if b in ['yes', 'y', '1', 'true', "True", "t", "T"]:
        return True
    if b in ['no', 'n', '0', 'false', "False", "f", "F"]:
        return False

class ArgumentParser(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.argparser = argparse.ArgumentParser(conflict_handler='resolve')
        self._args = None
        self.will_change = True

        self.argparser.add_argument('--is_extranet', default=False, type=parser_boolean, help="The network type used: intranet or extranet")
        self.argparser.add_argument('--sm_ip', default=get_cur_ip(), type=str,  help="The ip of the service mgr service")
        self.argparser.add_argument('--is_https', default=True, type=parser_boolean,  help="Is use http ssl connection")
        self.argparser.add_argument('--logger_level', default=INFO, type=str,  help="Default logger level")

    def get_argparser(self):
        return self.argparser

    @property
    def args(self):
        if self.will_change or not self._args:
            self._args = self.argparser.parse_args()
        return self._args