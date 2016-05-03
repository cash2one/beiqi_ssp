#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-5-7

@author: Jay
"""
import platform
import os
import psutil
from gevent import subprocess

def find_process_path(cmd):
    ls = cmd.strip().replace("\\", "/").split(" ")
    for data in ls:
        if "start.py" in data:
            return data
    return ""

def kill_process_by_cmd(kill_cmd_path):
    sys_platform = platform.system()
    if sys_platform == 'Windows':
        handle = os.popen('TASKLIST /FI "IMAGENAME eq python.exe"')
    elif sys_platform == 'Linux':
        handle = os.popen('ps ax|grep python')

    p_str_ls = handle.read().split("\n")
    for p_str in p_str_ls:
        p_info_ls = p_str.strip().split(" ", 1)
        try:
            if sys_platform == 'Windows':
                if p_info_ls[0] != "python.exe":
                    continue
                pid = int(p_info_ls[1].strip().split(" ", 1)[0])
            else:
                pid = int(p_info_ls[0])
            p_obj = psutil.Process(pid)
        except:
            print "psutil.Process failed,p_info_ls:%s",p_info_ls
            continue
        cmd = " ".join(p_obj.cmdline())
        cmd_path = find_process_path(cmd)
        kill_cmd_path = find_process_path(kill_cmd_path)
        if cmd_path and kill_cmd_path == cmd_path:
            p_obj.terminate()
            print "kill process:%s!!!" % cmd
            continue


def start_process(path, args=""):
    print "prepare start_process,path:%s,args:%s" % (path, args)
    subprocess.Popen("python %s %s" % (path, args), shell=True)


def stop_process(path):
    print "prepare stop_process,path,",path
    kill_process_by_cmd(path)

