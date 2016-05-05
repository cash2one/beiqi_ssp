#coding:utf-8

import re
from convert import _cn_mobile_pat


COMMON_PATTERN = re.compile(r'^[_a-z\d]{6,16}$')

beiqi_keys = {
    # 贝启
    '7a1d64b4b13548638ea9e20a2ebd5467': {
        's': '12047d9abfee4f5f987fd57b38c70f20',
    },
    # 设备
    '58a0c1d064a54dc2904773e7ef404073': {
        'rc4_key': '708ff663110047fa9ae11b608ac0f7f2',
        's': 'd046bfc19b88473fb00688ead394c88f'
    }
}




#s: secret
#p: 帐号格式
#f: 短信发送函数名称
#sms_prefix: 短信产品名
#sms_switch: 短信开关
#opt_mask: 权限覆盖，需求变更导致原始key不满足要求
#tr: 翻译语种


oem_accounts = {
    # 贝启
    '7a1d64b4b13548638ea9e20a2ebd5467': {
        's': '12047d9abfee4f5f987fd57b38c70f20',
    },
}
