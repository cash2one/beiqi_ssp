#coding: utf-8


from util.redis.redis_client import Redis
from util.stream_config_client import load as conf_load


_redis_conf = dict(conf_load('redis.ini')).get('redis.ini')
baidu_api_redis = Redis(_redis_conf.get('cloud_push', 'url'))


def set_api_key(app_id, api_key, secret_key):
    baidu_api_redis.send_multi_cmd(('set', ':'.join(('appid', app_id, 'apikey')), api_key),
                                   ('set', ':'.join(('appid', app_id, 'secretkey')), secret_key))


def init_app():
    app_id = raw_input('app id:')
    api_key = raw_input('API Key:')
    secret_key = raw_input('Secret Key:')
    set_api_key(app_id, api_key, secret_key)
    
    #不用在此处设置ios证书，因为实际上百度api也是上传证书内容到其服务器
    #与在百度管理后台设置效果一样
    
    print('初始化成功')


if __name__ == '__main__':
    init_app()
