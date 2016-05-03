/**
 * Created by Jay on 2015-11-2.
 */


SmartHome.Common.Img.reload = function(img){
    //重新加载图片，用于刷新验证码
    if(img.tagName == "IMG"){
        img.src=img.src+'?'+new Date().getSeconds()
    }
};

SmartHome.Common.Img.reloads = function(imgs){
    // 重载
    if( imgs instanceof HTMLCollection){
        for(var index= 0,length = imgs.length;index<length;index++){
            var img = imgs[index];
            SmartHome.Common.Img.reload(img)
        }
    }
};