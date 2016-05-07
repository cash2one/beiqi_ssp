#!/bin/sh

ps ax | grep "mq:host" | awk '{print $5}' | xargs killall
ps ax | grep "mq:" | awk '{print $1}' | xargs kill
