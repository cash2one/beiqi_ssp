# coding=utf-8
"""
實現scheduler,取代apscheduler和gevent的不兼容問題
Created on 2015-4-21
@todo:调度器
@author: Jay
"""
import datetime
import logging
import traceback

import gevent

from utils.meta.singleton import Singleton
from utils.wapper.stackless import gevent_adaptor


class LoopingCall(object):
    """
    间隔调用
    """
    def __init__(self, seconds, func, *args, **kwargs):
        """
        @param seconds:间隔时间(秒)
        @param func:回调函数
        @param now:是否立马调用
        """
        self._stop_flag = False
        self.greenlet = None
        self.seconds, self.args, self.kwargs = seconds, args, kwargs
        self.func = func
         
    def start(self):
        if not self._stop_flag:
            self.greenlet = gevent.spawn(self.__loop)
        
    def stop(self):
        if not self.greenlet:
            return
        self._stop_flag = True
        
    def __loop(self):
        while True:
            if self._stop_flag:
                return
            gevent.sleep(self.seconds)
            # 醒来的时候需要判断下，在睡眠这段时间是否有被停止
            if self._stop_flag:
                return
            try:
                self.func(*self.args, **self.kwargs)
            except:
                logging.error("args = %s, kwargs = %s \n %s", self.args, self.kwargs, traceback.format_exc())


class CronCall(object):
    """
    条件调用
    """
    def __init__(self, cron, func, *args, **kwargs):
        self.cron, self.func = cron, func
        self.args, self.kwargs = args, kwargs
        self.triggle = False
        
    def triggle_cron_job(self, now):
        ### 这里有潜在bug，如果设定hour=22，将触发2次函数调用
        for key, value in self.cron.items():
            if value is None:
                continue
            if key == 'weekday' and now.weekday() != value:
                self.triggle = False
                return
            if getattr(now, key) != value:
                self.triggle = False
                return
        if self.triggle:    # 上次满足触发条件
            return
        
        self.triggle = True  # 设置触发标识
        self.func(*self.args, **self.kwargs)


class DateCall(CronCall):
    """
    定点调用
    """
    def __init__(self, dt, func, finish_lambda=None, *args, **kwargs):
        if not isinstance(dt, datetime.datetime):
            assert dt, "dt:%s is not datetime" % dt
            
        cron = {"year": dt.year,
                "month": dt.month,
                "day": dt.day,
                'hour': dt.hour,
                'minute': dt.minute,
                'second': dt.second}
        super(DateCall, self).__init__(cron, func, *args, **kwargs)
        if finish_lambda:
            self.finish_lambda = finish_lambda
        
    def triggle_cron_job(self, now):
        if self.triggle:
            return
        
        super(DateCall, self).triggle_cron_job(now)

        if self.triggle:
            if self.finish_lambda:
                self.finish_lambda()
            
    
class Jobs(object):
    """
    计划任务
    """
    __metaclass__ = Singleton
    LoopTime = 0.49    # loop时间为

    def __init__(self):
        self.cron_job, self.inter_job = set(), set()
        self.main_loop = LoopingCall(self.LoopTime, self._loop)
        self._start_flag = False
        self.__remove_jobs = []

    @gevent_adaptor(use_join_result=False)
    def start(self):
        if self._start_flag:
            return
        self.main_loop.start() 
        for job in self.inter_job:
            job.start()
            
        self._start_flag = True
         
    def stop(self):
        self.main_loop.stop()
        for job in self.inter_job:
            job.stop()
        
        self._start_flag = False
        
    def add_interval_job(self, seconds, func, *args, **kwargs):
        """
        增加间隔任务
        @param func:回调函数
        @param seconds:间隔时间(秒)
        """
        obj = LoopingCall(seconds, func, *args, **kwargs)
        self.inter_job.add(obj)
        if self._start_flag:
            obj.start()
        return obj
        
    def add_cron_job(self, func, year=None, month=None, day=None,
                     weekday=None, hour=None, minute=None, second=None, **options):
        """
        条件任务
        @param func:回调函数
        @param year:
        @param month:
        @param day:
        @param weekday:
        @param hour:
        @param minute:
        """
        args, kwargs = options.get("args", []), options.get("kwargs", {})
        obj = CronCall({"year": year,
                        "month": month,
                        "day": day,
                        "weekday": weekday,
                        'hour': hour,
                        'minute': minute,
                        'second': second}, func, *args, **kwargs)
        self.cron_job.add(obj)
        return obj
    
    def add_date_job(self, func, date_time, finish_lambda=None, **options):
        """
        定时任务
        @param func:回调函数
        @param date_time:调用函数
        @param finish_lambda:完成lambda
        """
        args, kwargs = options.get("args", []), options.get("kwargs", {})
        obj = DateCall(date_time, func, finish_lambda, *args, **kwargs)
        self.cron_job.add(obj)
        return obj
    
    def remove_job(self, job):
        # 插入删除队列，解决_loop的时候，改变cron_job set元素个数的问题
        self.__remove_jobs.append(job)
        
    def __do_remove_job(self):
        if not self.__remove_jobs:
            return
        for job in self.__remove_jobs:
            if isinstance(job, LoopingCall):
                job.stop()
                self.inter_job.remove(job)
            elif isinstance(job, CronCall):
                self.cron_job.remove(job)
            elif isinstance(job, DateCall):
                self.cron_job.remove(job)
        self.__remove_jobs = []
        
    def _loop(self):
        now = datetime.datetime.now()
        for cron_obj in self.cron_job:
            cron_obj.triggle_cron_job(now)
        
        self.__do_remove_job()