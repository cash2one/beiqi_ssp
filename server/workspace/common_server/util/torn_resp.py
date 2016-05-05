#coding:utf-8


try:
    import simplejson as json
except ImportError:
    import json


def jsonify(r, p=None, d=None):
    """
    :param r: result
    :param p: payload
    :param d: detail string
    """
    assert isinstance(r, (int, bool))

    rt = {'r': int(r)}
    if p:
        assert isinstance(p, (dict, tuple, list))
        rt.update(dict(p=p))
    if d:
        assert isinstance(d, basestring)
        rt.update(dict(d=d))

    return json.dumps(rt)
