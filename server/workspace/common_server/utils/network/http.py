#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-25

@author: Jay
"""
from gevent import monkey
monkey.patch_all()

import os
import urllib2
import sys
from tornado import web
from tornado.web import RequestHandler, url
from tornado.wsgi import WSGIApplication
from gevent.wsgi import WSGIServer
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from utils.wapper.web import web_adaptor
from utils.wapper.stackless import gevent_adaptor
from utils import logger
from utils.service_control.setting import PT_HTTP, PT_HTTPS
from utils.network import PING_RESPONSE, RpcServer, RpcClient
from utils.route import Route
from utils.comm_func import import_handlers
from utils import __path__ as utils_paths


class HttpRpcHandler(RequestHandler):
    """
    HttpRpc回调处理类
    """
    _sessions_ = {}

    def render_string(self, template_name, **context):
        """
        字符串渲染
        :param template_name:
        :param context:
        :return:
        """
        if self.application.jinja_env:
            template = self.application.jinja_env.get_template(template_name,
                                                               parent=self.get_template_path())
            context['auto_reload'] = False
            return template.render(**context)
        else:
            RequestHandler.render_string(self, template_name, **context)

    def get(self, *args, **kwargs):
        """
        http get 请求
        :param args:
        :param kwargs:
        :return:
        """
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        http post 请求
        :param args:
        :param kwargs:
        :return:
        """
        return self.get(*args, **kwargs)

    @web_adaptor()
    def options(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT')
        self.set_header('Access-Control-Allow-Headers', 'Accept, Content-Type, Authorization, ID')
        return

    def get_request_ip(self):
        """
        获取请求ip
        :return:
        """
        return self.request.remote_ip

    def reponse_msg(self, msg, url=None):
        """
        url消息提示跳转
        :param msg: 需要提示的消息
        :param url: 跳转的url
        :return: None
        """
        msg_dic = {"msg":msg}
        if url:
            msg_dic["url"] = url
        self.render("auto_refresh.html", **msg_dic)

    def get_current_user(self):
        return self.get_secure_cookie('username',None)




class HttpPingHandle(HttpRpcHandler):
    """
    http ping 处理器
    """
    @web_adaptor(use_json_dumps=False)
    def get(self):
        """
        Http get 请求
        """
        return PING_RESPONSE

    def post(self):
        return self.get()


class DocHandle(HttpRpcHandler):
    """
    文档处理器
    """
    @web_adaptor(use_json_dumps=False)
    def get(self):
        """
        http get 请求
        :return:
        """
        service_type = sys.argv[0].replace("\\", "/").split("/")[-2]
        print "service_type,",service_type
        doc_path = os.path.join(os.path.dirname(sys.argv[0]),
                                'doc',
                                '%s.html' % service_type)
        return open(doc_path).read()

    def post(self):
        return self.get()


class SetLoggerLevelHandle(HttpRpcHandler):
    """
    设置日志等级
    """

    @web_adaptor(use_json_dumps=False)
    def get(self, logger_level):
        """
        Http get 请求
        """
        logger.set_logger_level(logger_level)
        return {"result": 0}

    def post(self, *args, **kwargs):
        """
        http post 请求
        """
        return self.get(*args, **kwargs)


class HttpRpcServer(RpcServer, WSGIApplication):
    """
    HttpRpc服务器
    """
    # 静态资源路径列表
    static_paths = [{"name": "common_static",  "uri": r"/static/(.+)", "path": os.path.join(utils_paths[0], "web", "static")},
                    {"name": "logic_static",   "uri": r"/logic/static/(.+)",       "path": os.path.join(os.path.dirname(sys.argv[0]), "logic", "web", "static")},
                    {"name": "favicon_static", "uri": r'/(favicon.ico)',     "path": os.path.join(utils_paths[0], "web", "static")}]

    settings = {"template_path": [os.path.join(utils_paths[0], "web", "template"),
                                  os.path.join(os.path.dirname(sys.argv[0]), "logic", "web", "template")],
                "cookie_secret": "SZUzonpBQIuXE3yKBtWPre2N5AS7jEQKv0Kioj9iKT0="}

    ssl_args = {"certfile": os.path.join(utils_paths[0], "CA", "server.crt"),
                "keyfile": os.path.join(utils_paths[0], "CA", "server.key")}

    def __init__(self, port, is_https):
        WSGIApplication.__init__(self, self._gen_handlers(), "", **self.settings)
        self.jinja_env = self._gen_jinja_env()
        super(HttpRpcServer, self).__init__(PT_HTTPS if is_https else PT_HTTP,
                                            port,
                                            WSGIServer(('', port), self, **self.ssl_args if is_https else {}))

    def _gen_jinja_env(self):
        """
        获取jinja环境参数
        :return:
        """
        jinja_env = Environment(loader=FileSystemLoader(self.settings['template_path']),
                                        auto_reload=True,
                                        autoescape=False)

        jinja_env.filters['lt_gt'] = lambda s: s.replace('<', '&lt;').replace('>', '&gt;')
        jinja_env.globals['settings'] = self.settings
        return jinja_env

    def _gen_handlers(self):
        """
        获取urlhandlers
        :return:
        """
        # import handlers
        handler_path = os.path.join(os.path.dirname(sys.argv[0]), "logic", "web", "handler")
        import_path = "logic.web.handler"
        import_handlers(handler_path, import_path)

        # register handlers
        handlers = [web.url(dic['uri'], web.StaticFileHandler, dict(path=dic['path']), name=dic['name'])
                    for dic in self.static_paths]

        handlers += Route.routes()

        handlers += [url(r"/ping", HttpPingHandle, {}, "ping handler")]
        handlers += [url(r"/set_logger_level", SetLoggerLevelHandle, {}, "Set Logger Level handler")]
        handlers += [url(r"/doc", DocHandle, {}, "Doc handler")]
        return handlers


class HttpRpcClient(RpcClient):
    """
    HttpRpc客户端
    """
    def __init__(self, host=None, port=None, ssl=False):
        self.host, self.port = host, port
        self.ssl = ssl

    def __get_full_url(self, url):
        """
        获取完整的可访问的url
        :param url: url链接，有可能只是接口
        :return:
        """
        protocol = "https" if self.ssl else "http"
        return '%s://%s:%s/%s' % (protocol, self.host, self.port, url) \
            if self.host and self.port \
            else url

    def _rpc_fetch(self, url, headers={}, body=None, method=None):
        """
        rpc函数调用实现
        :param url: url
        :param headers: headers
        :param body: body
        :param method: mothod
        :return:
        """
        full_url = self.__get_full_url(url)
        req = urllib2.Request(full_url, body, headers)
        if method:
            req.get_method = lambda:method

        try:
            result = urllib2.urlopen(req).read()
        except Exception, e:
            logger.error("HttpRpcClient::_rpc_fetch failed, url:%s headers:%s body:%s msg:%s" % (full_url, headers, body, e.message))
            raise
        if isinstance(result, Exception):
            raise result
        return result

    @gevent_adaptor()
    def fetch_async(self, url, headers={}, body=None, method=None):
        """
        协程非阻塞调用
        :param url: url
        :param headers: headers
        :param body:  body
        :param method:  mothod
        :return:
        """
        return self._rpc_fetch(url, headers, body, method)

    def fetch_sync(self, url, headers={}, body=None, method=None):
        """
        阻塞调用
        :param url: url
        :param headers: headers
        :param body:  body
        :param method:  mothod
        :return:
        """
        return self._rpc_fetch(url, headers, body, method)
