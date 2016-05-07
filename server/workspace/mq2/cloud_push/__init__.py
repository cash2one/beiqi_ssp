#coding:utf-8


from ios_client import invoke as ios_invoke
from baidu.baidu_client import invoke as baidu_invoke
from jpush.jpush_client import invoke as jpush_invoke
from gcm_client import invoke as gcm_invoke


def find_push(platform, bundle_id_channel):
    """
    :param bundle_id_channel: 水果bundle_id或者安卓第三方通道
    """
    if 'ios' == platform:
        return ios_invoke
    if 'baidu' == bundle_id_channel:
        return baidu_invoke
    if 'jpush' == bundle_id_channel:
        return jpush_invoke
    if 'gcm' == platform:
        return gcm_invoke

    return None