#coding:utf-8


from crypto_rc4 import encrypt as rc4_encrypt
from Crypto.Hash import HMAC, SHA
from urllib import urlencode


CIPHER_KEY = '5f7b51f6fcb546b5aceda49002d37eac'


def __is_cdma(bs_one):
    mcc = bs_one.get('mcc')
    mnc = bs_one.get('mnc')
    if mnc is None:
        return None
    return 460 == mcc and 3 == mnc


def __build_gsm_bts(bs_dict):
    """
    构建gsm基站格式
    """
    assert bs_dict and isinstance(bs_dict, dict)
    return ','.join((str(bs_dict.get(k, '')) for k in ('mcc', 'mnc', 'lac', 'cellid', 'rssi')))


def __build_cdma_bts(bs_dict):
    #设备上报的log&lat容易解析出错，暂时屏蔽
    return ','.join((str(bs_dict.get(k, '')) for k in ('sid', 'nid', 'bsid', 'log_mask', 'lat_mask', 'rssi')))


def __build_wifi(wifi_dict):
    assert wifi_dict and isinstance(wifi_dict, dict)
    return ','.join((str(wifi_dict.get(k)) for k in ('mac', 'rssi', 'ssid')))


def build_url(auth_key, pid, bs_list, wifi_list,
              dev_loc_log=None, dev_loc_lati=None, dev_loc_accuracy=None,
              navi_host='http://apilocate.amap.com/position?',
              use_proxy=False,
              proxy_host=''):
    """
    构建高德接口url

    :param auth_key: 认证key
    :param pid: 高德要求唯一即可，此处用pid替代
    :param dev_loc_log: 设备获取的东经，可选
    :param dev_loc_lati: 设备获取的北纬，可选
    :param dev_loc_accuracy: 设备获取的精度，可选
    :param navi_host: 高德服务器地址
    :param use_proxy: 是否我司代理服务器使用
    :param proxy_host: 代理地址
    """
    #基站或wifi必须有其一
    if not (bs_list or wifi_list):
        return None
    if not (pid and isinstance(pid, str)):
        return None
    if wifi_list:
        if not isinstance(wifi_list, (list, tuple)):
            return None
    if bs_list:
        if not isinstance(bs_list, (list, tuple)):
            return None
        cdma = __is_cdma(bs_list[0])
        if cdma is None:
            return None
        #基站信息
        if not cdma:
            bts = __build_gsm_bts(bs_list[0])
            nearbts = '|'.join((__build_gsm_bts(d) for d in bs_list[1:]))
            #是否带入临近基站信息
        else:
            #cdma没有临近基站
            bts = __build_cdma_bts(bs_list[0])
            nearbts = '|'.join((__build_cdma_bts(d) for d in bs_list[1:]))

    params = {
        'accesstype': '0' if bs_list else '1',
        'imei': pid,
        'output': 'json',
        'key': auth_key,
    }
    if dev_loc_log:
        if dev_loc_lati and dev_loc_accuracy and isinstance(dev_loc_log, (int, float)) \
                and isinstance(dev_loc_lati, (int, float)) and isinstance(dev_loc_accuracy, (int, float)):
            params.update({'gps': '{0},{1}|{2}'.format(dev_loc_log, dev_loc_lati, dev_loc_accuracy)})
        else:
            return None

    if 'cdma' in locals():
        params.update({'cdma': str(int(locals().get('cdma')))})
    [params.update({k: locals().get(k)}) for k in ('bts', 'nearbts') if k in locals()]
    if wifi_list:
        params.update({'smac': ''})
        params.update({'macs': '|'.join((__build_wifi(w) for w in wifi_list))})

    url = navi_host + '&'.join(('{0}={1}'.format(k, v) for k, v in params.iteritems()))
    if not use_proxy:
        return url

    if not proxy_host:
        return None

    return proxy_host + urlencode({
        'a': rc4_encrypt(url, CIPHER_KEY),
        's': HMAC.new(CIPHER_KEY, url, SHA).hexdigest(),
    })
