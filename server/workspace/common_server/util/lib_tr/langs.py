#coding:utf-8

import re

ARG_PATTERN = re.compile(r'\{(?P<index>\d+)\}')
DEFAULT_LANG = 'chs'


#模板
sms_template = {
    #cat
    0:  '{0}是您本次身份校验码，15分钟内有效。',
    1:  '{0}验证码：{1}。手机号为{2}的用户请求绑定手表，若同意，请将该码告之，15分钟内有效。',
    2:  '您的帐号{0}正在重设密码，请输入验证码:{1}，若不是您本人发出，请忽略。',
    3:  '您的宝贝于 {0} 发出紧急求救呼叫，请立即收听。温馨提醒：短按即可记录声音，以免误触紧急求救。',
}

push_template = {
    'dev_act': {
        'chs': '设备激活成功',
        'vn': 'Kích hoạt thành công',
    },
    'fb_done': {
        'chs': '设备指令已处理完成',
        'vn': 'Kác yêu cầu đã được xử lý',
    },
    'fb_wait': {
        'chs': '设备指令等待处理',
        'vn': 'Yêu cầu của bạn đang chờ xử lý',
    },
    'fb_busy': {
        'chs': '设备繁忙，请稍后重试',
        'vn': 'Thiết bị đang bận, hãy thử lại',
    },
    'fb_dft': {
        'chs': '设备指令执行中，请稍等',
        'vn': 'Kêu cầu của bạn đang được xử lý, hãy chờ',
    },
    'loc_chg': {
        'chs': '手表充电中{0}%',
        'vn': 'Đồng hồ đang sạc {0}%',
    },
    'loc_bat_low': {
        'chs': '手表电量过低，仅剩{0}%，请及时充电',
        'vn': 'Pin đồng hồ sắp hết, còn lại “{0}%”, hãy kết nối sạc'
    },
    'loc_ok': {
        'chs': '定位成功',
        'vn': 'ĐỊnh vị thành công',
    },
    'loc_fail': {
        'chs': '定位失败',
        'vn': 'ĐỊnh vị thất bại',
    },
    'loc_unknown': {
        'chs': '陌生道路',
        'vn': 'Khu vực lạ',
    },
    'rec_rmt': {
        'chs': '【录音成功】已完成对宝贝的录音',
        'vn': '[Ghi âm thành công] đã ghi âm giọng nói của bé'
    },
    'rec_hello': {
        'chs': '【录音提醒】宝贝发来一段最新录音',
        'vn': '[Thông báo có bản ghi] bé gửi bản ghi âm tới'
    },
    'rec_sos': {
        'chs': '【SOS录音提醒】宝贝发来紧急求救录音，建议您立即收听',
        'vn': 'Thông báo bản ghi SOS/ bé gửi bản ghi âm khẩn cấp, hãy nghe ngay'
    },
    'rec_dft': {
        'chs': '录音成功',
        'vn': 'Ghi âm thành công',
    },
    'zone_left': {
        'chs': '宝贝离开{0}',
        'vn': 'Bé đã rời khỏi {0}',
    },
    'zone_dischg': {
        'chs': '手表电量仅{0}%，请及时充电',
        'vn': 'Pin đồng hồ còn {0}%, hãy cắm sạc'
    },
    'zone_arrive': {
        'chs': '宝贝到达{0}',
        'vn': 'Bé đã đến {0}',
    },
    'zone_unkzm': {
        'chs': '宝贝处于{0}，已离开安全区{1}',
        'vn': 'Bé đang ở {0}, ngoài khu vực an toàn'
    },
    'zone_unkzst': {
        'chs': '宝贝已在{0}逗留{1}，请关注',
        'vn': 'Bé đang ở {0}, hãy để ý theo dõi',
    },
}

feeds_template = {
    #时间线，上传双向文件
    'feeds_bi': {
        'chs': '上传了文件',
        'vn': ''
    },
    'feeds_bonus_incre': {
        'chs': '增加了{0}粒爱心',
        'vn': '',
    },
    'feeds_sleep': {
        'chs': '手表进入睡眠',
        'vn': '',
    },
    'feeds_hello': {
        'chs': '{0}',
        'vn': '{0}',
    },
    'feeds_time_format': {
        'chs': '手表设置为{0}小时制',
        'vn': '{0}'
    },
    'feeds_record': {
        'chs': '发起一次录音',
        'vn': '',
    },
    'feeds_normal_loc': {
        'chs': '发起一次定位',
        'vn': '',
    },
    'feeds_voc_study': {
        'chs': '选取了{0}个英文单词',
        'vn': '{0}',
    },
    'feeds_urgent_loc': {
        'chs': '发起一次紧急定位',
        'vn': '',
    },
    'feeds_shutdown': {
        'chs': '手表关机',
        'vn': '',
    },
    'feeds_bonus_top': {
        'chs': '爱心清零',
        'vn': '',
    },
}


date_langs = {
    'chs': '%Y-%m-%d %H:%M:%S',
    'en': '%d/%m/%Y %H:%M:%S',
    'vn': '%d/%m/%Y %H:%M:%S',
}

time_langs = {
    'chs': (
        ('小时', 3600),
        ('分', 60),
        ('秒', 1),
    ),
    'vn': (
        (' giờ ', 3600),
        (' phút ', 60),
        (' giây', 1),
    ),
}


_mcc_map = {
    460: 'chs',
    #越南
    452: 'vn',
    #意大利
    222: 'it',
}


def _cal_args(langs):
    def __():
        for k, v in langs.iteritems():
            l = []
            for abbr, text in v.iteritems():
                arg_len = len(set((int(_) for _ in ARG_PATTERN.findall(text))))
                l.append((abbr, arg_len))

            yield k, dict(l)

    for k, d in __():
        #以中文参数个数为标准
        #其他语言如超出则认为错误
        #不要求完全相等
        chs_param_count = d.get(DEFAULT_LANG)
        if any((True for country, count in d.iteritems() if count > chs_param_count)):
            raise ValueError('some lang arg too much: {0}, {1}'.format(k, d))
        langs[k].update({'_len': d.values()[0]})


lang_cats = ('chs')
#_cal_args(sms_template)
_cal_args(push_template)
_cal_args(feeds_template)
