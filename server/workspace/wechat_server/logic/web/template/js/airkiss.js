wx.config({			beta: true,		    debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。		    appId: $("#appId").val(), // 必填，公众号的唯一标识		    timestamp: $("#timestamp").val(), // 必填，生成签名的时间戳		    nonceStr: $("#nonceStr").val(), // 必填，生成签名的随机串		    signature: $("#signture").val(),// 必填，签名，见附录1		    jsApiList: ["configWXDeviceWiFi"] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2		});wx.ready(function() {	$(".connectWifi").click(function(){		wx.invoke('configWXDeviceWiFi', {}, function(res) {			alert(res.err_msg);			if (res.err_msg == 'configWXDeviceWiFi:ok') {				alert("配置成功");				WeixinJSBridge.call('closeWindow');			} else if (res.err_msg == 'configWXDeviceWiFi:fail') {				alert("配置超时");			}			console.log(JSON.stringify(res));		});	});});wx.error(function(res) {	alert(res.errMsg);});