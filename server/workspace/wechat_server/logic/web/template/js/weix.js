$(function(){  
    var name_all;
    var new_nick;

    $(".wei_ul li dl").click(function(){//点击下拉框
        $(this).parent().find('div.select').removeClass("menu_chioce");
        $(".menu_chioce").slideUp(); 
        $(this).parent().find('div.select').slideToggle();
        $(this).parent().find('div.select').addClass("menu_chioce");
    });

    $(".confirm_x").click(function(){//更改昵称,确认按键
        basic_infor();
        $(".weui_dialog_confirm").hide();
        var paddleft = name_all.replace(/[^0-9]/ig, "");
        var num = parseInt(paddleft); //获取设备num
        eachname("change_name")//判断data，成功后更改
        console.log("设备号的id: " + num);//获取的设备号
        console.log("微信用户id: " + user_id);//获取的用户id
        console.log("更改后的新昵称: "+ new_nick);//获取chance_name要更改的新昵称，提交后台
        console.log("全部用户信息: " + datat);
        //提交后台数据,data数据num设备号,chance_name新昵称,datat微信用户所有信息,user_id微信用户的id
         $.ajax({
             url:"url",
             data:{new_nick:new_nick,username:user_id, gid:num},//传送数据参数
             type:"GET",//数据传输类型POST,GET
             success:function(data){
                 eachname("change_name")//判断data，成功后更改
             }
         })
    });

    // 获取基本信息 star 用户的id
    basic_infor();
    function basic_infor(){
        //var servi_data = $(".data_all").text();
        //var arry = servi_data.split(" u'");
        //var newarry = arry.join("'");
        //var val = newarry.split("{u'");
        //var last_data = val.join("{'");
        //var datal = eval('(' + last_data + ')');
        //console.log("openid : " + datal.openid)//获取基本id
        //var datat = JSON.stringify(datal);//装换字符串
        user_id = $(".data_all").text();
    };
    
    $(".confirm").click(function(){//解除绑定按键
        basic_infor();
        var paddleft = name_all.replace(/[^0-9]/ig, "");
        var num = parseInt(paddleft);
        eachname("remove_equipment")//判断data成功，解绑成功
        //alert('num = ' + num);//num需要解绑的设备id
        //alert('user_id = ' + user_id);
        //提交后台数据,data数据num设备号,chance_name新昵称,datat微信用户所有信息,user_id微信用户的id
         $.ajax({
             url:"http://wechatapi.beiqicloud.com:8108/wechat/unbind",
             data:{username:user_id,gid:num},//传送数据参数
             type:"GET",//数据传输类型POST,GET
             success:function(data){
                 //alert(data);
                 eachname("remove_equipment")//判断data成功，解绑成功
             }
         })
    });

    getid(".weui_modify",".weui_dialog_confirm");
    getid(".weui_jiebang",".weui_dialog_jiebang");
    hide(".cancel_x",".weui_dialog_confirm");//点击取消修改昵称
    hide(".confirm",".weui_dialog_jiebang");//点击确定解绑
    hide(".cancel",".weui_dialog_jiebang");//点击取消解绑

    //隐藏跳出匡，divname点击的，nextname隐藏的
    function hide(divname,nextname){
        $(divname).click(function(){
            $(nextname).hide();
        });
    };

    //获取亲友圈id
    function getid(title,title_name){
        $(title).click(function(){
            $(".new_name").val("");
            $(title_name).show();
            $(".new_name").focus();//焦点聚焦输入框
            var name_id = $(this).parents('li').find('dd.nameid').text();
            name_all = name_id;
        });
    };

    //更改页面昵称，解除绑定条目确认键
    function eachname(name){
        $(".select").each(function(i,itme){
            var namene = $(".new_name").val();
            var old_val = itme.style.display;//获取显示的block           
            if(old_val == "block"){
                switch(name)
                {
                    case "change_name":
                      $(".wei_ul li").eq(i).find("dd.title").text(namene);//更改昵称到当前界面
                      new_nick = namene;
                      break;
                    case "remove_equipment":
                      $(".wei_ul li").eq(i).remove();//去除解绑的li页面样式
                      break;
                };
            };
        });
    }

    //获取用户id
    function basic_infor(){
        //var servi_data = $(".data_all").text();
        //var arry = servi_data.split(" u'");
        //var newarry = arry.join("'");
        //var val = newarry.split("{u'");
        //var last_data = val.join("{'");
        //var datal = eval('(' + last_data + ')');
        //datat = JSON.stringify(datal);//装换字符串全部信息提交
        //user_id = datal.openid;//获取设备号
        user_id = $(".data_all").text();

    };

}); 
   
