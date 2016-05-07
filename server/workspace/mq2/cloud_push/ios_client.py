#coding:utf-8


from utils import logger
from util.internal_forward.apple_push_encode import encode as apns_encode
from tornado.gen import coroutine
from util.internal_forward.gen_internal_client import GeneralInternalClient
from util.stream_config_client import load as conf_load
from util.convert import parse_ip_port


apns_client = GeneralInternalClient(parse_ip_port(dict(conf_load('apns.ini')).get('apns.ini').get('_default', 'host')))


@coroutine
def invoke(push_body, channel_args):
    """
    :param push_body: dict
    """
    try:
        if not (push_body and isinstance(push_body, dict)):
            logger.warn('ios_invoke push_body: {0}'.format(push_body))
            return
        if 3 != len(channel_args):
            logger.warn('invalid ios args: {0}'.format(channel_args))
            return

        alert = push_body.get('description')
        push_body = dict(((k, push_body.get(k)) for k in ('cb', 'f', 'id')))

        r = yield apns_client.forward(apns_encode(alert, push_body, *channel_args))
        logger.debug('ios result: %r' % r)
    except Exception, ex:
        logger.error('ios_push err: {0}'.format(ex), exc_info=True)