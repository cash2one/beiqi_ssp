#coding:utf-8
import msgpack
import json
from util.log_util import gen_log

def cms_pack(typ,dic_params):
    # 打包生产数据
    if not (typ and isinstance(typ, str)):
        gen_log.warn('cms typ invalid: %s' % type(typ))
        return
    if not (dic_params and isinstance(dic_params,dict)):
        gen_log.warn('cms data invalid')
        return

    return msgpack.packb(
        {
            'typ':typ,
            'params': json.dumps(dic_params,sort_keys=True,separators=(',',':'),ensure_ascii=False),
        }, use_bin_type=True
    )
