#!/bin/sh
wd="/home/"`whoami`"/codes/beiqi_css/mq2"
cd $wd
sh ./kill_mq.sh
rm -rf logs
sh ./host_run.sh
