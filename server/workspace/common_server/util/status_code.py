# coding: utf-8

import json
from utils import logger



def dump_status(code, msg=None):
    if msg:
        logger.debug(', '.join(('status={0}'.format(code), msg)))
    return json.dumps({'status': code})
