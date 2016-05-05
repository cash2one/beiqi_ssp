# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""

from tornado.web import url


class Route(object):

    _routes = {}

    def __init__(self, pattern, kwargs=None, name=None, host='.*$'):
        self.pattern = pattern
        self.kwargs = kwargs if kwargs else {}
        self.name = name if name else pattern
        self.host = host

    def __call__(self, handler_class):
        spec = url(self.pattern, handler_class, self.kwargs, name=self.name)
        self._routes.setdefault(self.host, []).append(spec)
        return handler_class

    @classmethod
    def routes(cls, application=None):
        if application:
            for host, handlers in cls._routes.items():
                application.add_handlers(host, handlers)
        else:
            return reduce(lambda x, y: x+y, cls._routes.values()) if cls._routes else []

route = Route
