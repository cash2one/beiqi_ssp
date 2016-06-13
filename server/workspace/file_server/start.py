#coding:utf-8
import site, os; site.addsitedir(os.path.dirname(os.path.realpath(__file__))); site.addsitedir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))); site.addsitedir(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "common_server"))
import platform
from setproctitle import setproctitle
import tornado.options
from tornado import httpserver
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application
from logic.write import WriteHandler
from logic.down_multi import MultiDownHandler
from logic.read import ReadHandler
from logic.delete import DeleteFileHandler
from setting import SERVICE_TYPE
from utils import logger

define("port", help="run on the given port", type=int, default=8106)
setproctitle(SERVICE_TYPE)

logger.init_log(SERVICE_TYPE, SERVICE_TYPE)


def main():
    tornado.options.options.logging = 'debug'
    tornado.options.parse_command_line()

    #主从分离后，读取从库mysql
    settings = {
        #最大内存上限100K
        'max_buffer_size': 102400,
    }

    app = Application(
        [
            ('/up', WriteHandler),
            ('/down', ReadHandler),
            ('/delete_file', DeleteFileHandler),
            ('/down_multi', MultiDownHandler),
        ],
        **settings
    )

    server = httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(0) if platform.system() == 'Linux'else server.start()

    logger.warn("start services for %s" % (SERVICE_TYPE))
    logger.warn("start listen on HTTP:%s" % (options.port))
    IOLoop.instance().start()


if __name__ == '__main__':
    main()