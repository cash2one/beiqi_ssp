/**
 * Created by Jay on 2015-10-30.
 */

SmartHome.Common.Ajax = function(method,url,data,success,failure){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4){
            if(xhr.status == 200){
                success.apply(this,arguments);
            }else{
                failure.apply(this,arguments)
            }
        }
    };
    xhr.open(method,url,true);
    if (data){
        xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    }
    xhr.send(data)
};

SmartHome.Common.bind = function(fn,context){
    // 简单的函数环境绑定函数
    return  function(){
        fn.apply(context,arguments)
    }
};