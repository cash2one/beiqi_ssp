pandora
#############################

版本: 0.0.1

1.简介
=============

pandora是一个逻辑服务查找服务器，功能主要是提供客户端后台服务动态查找功能


2.接口介绍
==============

pandora通过HTTP的固定20000接口访问：
	
	http:/192.168.1.110:20000 
	
	
2.1 帮助文档
--------------

	HTTP GET /doc

	Response:
		html帮助文档
	
	
2.2 列举所有的服务
--------------------

	HTTP GET /:

	Response:
		http的列表显示格式

        	
2.3 服务查找
--------------

	HTTP GET /services:
		service: 服务名，可为空

	Response:
		http的列表显示格式
		
2.4 选择一个服务
-----------------

	HTTP GET /locate:
		service: 服务类型名称

	Response::

		{
			"https"/"http": ""host:port",
			
			"xmpp": "JID",   可为空
		
		}
		

	如果没有该服务注册到pandora,将返回空
	
	
2.5 获取PublicKey:	
------------------------------------------
	HTTP GET /get_public_key:	
		
	Response(UJSON):
		File
		
		
2.6 查看设备类型
-------------------

	HTTP GET /device_type:

	Response:
		http的列表显示格式
		
2.7 服务的帮助文档
-------------------

	HTTP GET /service_doc:
		service: 服务类型名称

	Response:
		具体服务的html帮助文档
		
		
