#!/bin/sh

#tornado创建子进程为避免僵尸进程的产生
#对子进程有os.wait操作
#意味着如果有多个redis实例需要监听
#只能通过外部shell的方式执行

#关闭父子进程顺序如下
#0. kill -9 [父进程id]
#1. killall -9 [子进程名]

for x in `python load_conf.py`
do
    nohup python -O mq_host.py $x &
done
