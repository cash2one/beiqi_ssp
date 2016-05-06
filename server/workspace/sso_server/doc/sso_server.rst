register
#############################

版本: 0.0.1

1.简介
=============

register是一个注册服务器，功能主要是手机jid和设备jid的绑定解绑定等功能


2.接口介绍
==============

2.1 获取验证码
------------------------------------------
	HTTPS GET/POST /verify_code:	
		
		
	Response:
		Picture

2.2 用户登录:	
------------------------------------------
	HTTPS get/post /login:	
		verify_code: 验证码; 设备端可不传
		
		user_name: 字符串
		
		password: 字符串
		 
		type： 1=Phone, 2=Device, 3=Wechat
		
		param_sign: 服务器参数签名，字符串
		
	Response:
		'result':请见错误码说明, 
		
		'user_info':'user_info'(详见4数据模板)
		
		'access_token': 用户访问token

		'sign': 服务器名签名


		
2.3 用户注册
------------------------------------------
	HTTPS get/post  /register:	
		verify_code: 验证码
		
		user_name: 字符串
		
		password: 字符串
		
		des: 描述，字符串
		
		type： 1=Phone, 2=Device, 3=Wechat
		
		device_type: 设备类型，type是Device的时候，必须带
		
	Response:
		'result':请见错误码说明

		'sign': 服务器名签名
		
2.4 用户销户
------------------------------------------
	HTTPS get/post  /cancel:	
		verify_code: 验证码
		
		user_name: 字符串
		
		password: 字符串
		
		type： 1=Phone, 2=Device, 3=Wechat
		
	Response:
		'result':请见错误码说明

		'sign': 服务器名签名
		
		
2.5 获取用户信息:	
------------------------------------------
	HTTPS/TCP /get_users(UJSON):
		access_token: 访问token
			
		user_name_ls : ujson(["用户名1",,,,,])
		
	Response:
		'user_info_ls': ['user_info'(详见4数据模板),,,,]

		'result':请见错误码说明,

		'sign': 服务器名签名

		
2.6 验证token有效性:	
------------------------------------------
	TCP /verify_access_token(UJSON):	
		{
			'access_token': 访问token
			
		}
		
	Response:
		'result':请见错误码说明, 
		
		'validate':True or False

2.7 用户绑定设置
------------------------------------------
	HTTPS get/post  /set_user_banding:
		user_name: 申请绑定用户

		user_name_ls: 被绑定用户列表,ujson(["用户名1",,,,,])

	Response:
		'result':请见错误码说明

		'sign': 服务器名签名

2.8 用户解绑设置
------------------------------------------
	HTTPS get/post  /set_user_unbanding:
		user_name: 申请解绑用户

		user_name_ls: 被解绑用户列表,ujson(["用户名1",,,,,])

	Response:
		'result':请见错误码说明

		'sign': 服务器名签名
		
2.9 获取用户解绑列表
------------------------------------------
	HTTPS get/post  /get_user_banding:
		user_name: 申请用户


	Response:
		'roster_item': ['roster_item'(详见4数据模板),,,,]
	
		'result':请见错误码说明

		'sign': 服务器名签名

		
		
		

3. 错误码说明
===============

"""
SYSTEM ERROR CODE
"""

ERROR_SUCCESS = 0                           # 操作成功

ERROR_UNKNOWN_ERROR = 1                     # 未知错误

ERROR_PARAMS_ERROR = 2                      # 参数格式错误

ERROR_DB_ERROR = 3                          # 数据库操作错误

ERROR_ACCESS_TOKEN_ERROR = 4                # AccessToken错误

ERROR_VERIFY_CODE_ERROR = 5                 # 验证码错误

ERROR_SIGN_ERROR = 6                        # 参数签名出错

ERROR_SERVICE_START_ERROR = 7               # 服务器启动失败

ERROR_SERVICE_STOP_ERROR = 8                # 服务器关闭失败



"""
LOGIC ERROR CODE
"""

ERROR_OPER_NOT_PERMIT = 100                 # 操作不被允许,权限不够

ERROR_OPENFIRE_NEW_JID_FAIL = 101           # OPENFIRE 注册新JID失败

ERROR_USER_NAME_OR_PASSWORD_ERROR = 102     # 用户名或者密码错误

ERROR_USER_NAME_EXIST = 103                 # 用户名已经存在

ERROR_USER_NAME_NO_EXIST = 104              # 用户名不存在

ERROR_JID_OR_JID_PASS_ERROR = 105           # JID 获取JID 密码错误

ERROR_MXID = 106                            # MXID无效，没有JID，或者access_token过期

ERROR_JID_HAS_NOT_LOGIN = 107               # JID 还没有登录

ERROR_JID_ROSTER_UNSUBSCRIBE = 108          # JID 邀请添加roster被拒绝

ERROR_JID_ALREADY_IN_ROSTER = 109           # 被邀请者JID 已经在roster列表里面

ERROR_JID_NOT_IN_ROSTER = 110               # 被邀请者JID 不在被roster列表里面
 


4.数据模板
==============

user_info:{"user_name":用户名,"password":密码,"des":描述, 'jid':jabber id,'jid_pwd':JID密码, "type":类型}

roster_item:{'jid': JID, 'subscriptionType': roster关系, 'nickname': 别名, 'groups': 所属组字典}