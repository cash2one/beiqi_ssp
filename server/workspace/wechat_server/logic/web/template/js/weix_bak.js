$(function(){ //加载
    var name_all;
    var chance_name;
    //循环内容，如若数据是后台以json格式在前台显示，用js循环
    shebei("杨浩","09899");
    shebei("小智","09885");
    shebei("小明","09833");
    shebei("小三","09836");
    shebei("小李","09895");
    //微信用户 name循环的昵称，name_id循环的id
    function shebei(name,name_id){
        $('.wei_ul').append('<li><dl onclick="dl_up(this)"><dt><img src="images/title.jpg"></dt><dd class="title">' + name + '</dd><dd class="nameid">'+ name_id +'</dd></dl><div class="select"><a href="javascript:;" class="weui_modify" onclick="getoid(\'.weui_dialog_confirm\',this)"><img src="/static/images/xiugai.jpg"></a><a href="javascript:;" class="weui_jiebang" onclick="getoid(\'.weui_dialog_jiebang\',this)"><img src="/static/images/jiechu.jpg"></a></div></li>');
    }
}); 

    //下拉菜单
    function dl_up(that){
        $(that).parent().find('div.select').removeClass("menu_chioce");
        $(".menu_chioce").slideUp(); 
        $(that).parent().find('div.select').slideToggle();
        $(that).parent().find('div.select').addClass("menu_chioce");
    }

    //获取设备号
    function getoid(title_name,that){
            $(".new_name").val("");
            $(title_name).show();
            $(".new_name").focus();//焦点聚集input框
            var name_id = $(that).parents('li').find('dd.nameid').text();
            name_all = name_id;
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
                      chance_name = namene;
                      break;
                    case "remove_equipment":
                      $(".wei_ul li").eq(i).remove();//去除解绑的li页面样式
                      break;
                };
            };
        });
    }
    
    //解绑用户所绑定的设备
    function jiebang(){
        // basic_infor();
        $(".weui_dialog_jiebang").hide();
        var paddleft = name_all.replace(/[^0-9]/ig, "");
        var num = parseInt(paddleft);
        eachname("remove_equipment")//如果是其他条件需添加条件判断
        console.log("设备号的id: " + num);//获取的设备号
        // console.log("微信用户id: " + user_id);//获取的用户id
    }

    //确定按键，提交新昵称到后台
    function queding(){
            // basic_infor();
            $(".weui_dialog_confirm").hide();
            var paddleft = name_all.replace(/[^0-9]/ig, "");
            var num = parseInt(paddleft); //获取设备num
            eachname("change_name")//如果是其他条件需添加条件判断
            if(chance_name == ""){//判断新昵称是否为空
                console.log("新昵称为空值，请输入新昵称！"); 
                return;
            }
            console.log("设备号的id: " + num);//获取的设备号
            // console.log("微信用户id: " + user_id);//获取的用户id
            console.log("更改后的新昵称: "+ chance_name);//获取chance_name要更改的新昵称，提交后台
            console.log("全部用户信息: " + datat);
            //提交后台数据,data数据num设备号,chance_name新昵称,datat微信用户所有信息,user_id微信用户的id
            // $.ajax({
            //     url:"http://192.168.2.168:81/devmgmt/import_dev/",
            //     data:{num:num,chance_name:chance_name,datat:datat,user_id:user_id},//传送数据参数
            //     type:"POST",//数据传输类型POST,GET
            //     success:function(data){
            //         console.log(data);
            //     }
            // })
    }

    //取消按键
    function hide(nextname){
        $(nextname).hide();
    };

    // 获取基本信息 star 用户的id
    // function basic_infor(){
    //     var servi_data = $(".data_all").text();
    //     var arry = servi_data.split(" u'");
    //     var newarry = arry.join("'");
    //     var val = newarry.split("{u'");
    //     var last_data = val.join("{'");
    //     var datal = eval('(' + last_data + ')');
    //     datat = JSON.stringify(datal);//装换字符串全部信息提交
    //     user_id = datal.openid;//获取设备号
    // };
    