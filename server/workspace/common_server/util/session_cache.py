#coding: utf-8


import time
from utils import logger


class SessionCache(object):
    def __init__(self, duration=None, precision=None):
        # 时间戳精度
        self._ts_precision = precision or 1000000
        # 单位：秒
        self._sid_duration = duration or (180 * self._ts_precision)
        self.cache = {}

    def set_duration(self, duration):
        if isinstance(duration, int) and duration >= 0:
            self._sid_duration = duration


    def set_precision(self, precision):
        if isinstance(precision, int) and precision >= 0:
            self._ts_precision = precision


    def get_timestamp(self):
        """
        :return: int type, value = timestamp * 1000000, keeping all numbers after the decimal point
        """
        now = int(time.time() * self._ts_precision)
        return now


    def is_sid_expired(self, sid):
        """
        有效时间默认为3分钟
        :param sid:
        :return:
        """
        now = self.get_timestamp()
        return now > int(sid) + self._sid_duration


    def new_session(self, d=None):
        # 1 <= sid <= 100
        now = self.get_timestamp()
        if len(self.cache) >= 500:
            self.cache = {k:v for k, v in self.cache.iteritems() if not self.is_sid_expired(k)}

        if d is None:
            d = {}

        sid = str(now)

        self.cache[sid] = d

        return sid


    def del_session(self, sid):
        if sid in self.cache:
            del self.cache[sid]


    def update(self, sid, d):
        self.cache[sid].update(d)


    def get_session_cache(self, sid):
        if self.is_sid_expired(sid):
            logger.debug('sid: {0} expired'.format(sid))
            return None

        d = self.cache.get(sid)
        if d is None:
            logger.debug('sid: {0} cache is None. cache {1}'.format(sid, self.cache))

        return self.cache.get(sid)
