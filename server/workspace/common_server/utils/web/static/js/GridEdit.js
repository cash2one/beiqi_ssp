/** 
* JS实现可编辑的表格   
* 用法:EditTables(tb1,tb2,tb2,......); 
* Create by Senty at 2008-04-12 
**/

//设置多个表格可编辑  
function EditTables(){
    for(var i=0;i<arguments.length;i++){
        SetTableCanEdit(arguments[i]);
    }
}

//设置表格是可编辑的
function SetTableCanEdit(table){
    for(var i=1; i<table.rows.length;i++){
        SetRowCanEdit(table.rows[i]);
    }
}

function SetRowCanEdit(row){
    for(var j=0;j<row.cells.length; j++){
    //如果当前单元格指定了编辑类型，则表示允许编辑
        var editType = row.cells[j].getAttribute("data-EditType");
        if(!editType){
            editType = row.parentNode.rows[0].cells[j].getAttribute("data-EditType");
        }
        if(editType){row.cells[j].onclick = function (){EditCell(this)}}
        }
}

//设置指定单元格可编辑
function EditCell(element){
    var editType = element.getAttribute("data-EditType");
    if(!editType){
       //如果当前单元格没有指定，则查看当前列是否指定
        editType = element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute("data-EditType");
    }
    switch(editType){
        case "TextBox":
            CreateTextBox(element, element.innerHTML);
            break;
        case "DropDownList":
            CreateDropDownList(element);
            break;
        case 'AreaBox':
            CreateAreaBox(element,element.innerText);
            break;
        case 'ModalBox':
            CreateModalBox(element.firstChild);
            break;
        default:
            break;
    }
}

function CreateModalBox(element){
    // 这是高度依赖 Bootrap 和 HTML/JS 的函数, 高度耦合，无法独立的，专门为页面设计，
    var value = element.getAttribute('data-value')||element.innerHTML;
    value = value.replace(/&lt;/g,'<');
    value = value.replace(/&gt;/g,'>');
    $("#ModalBox").modal({
        'backdrop':false,
        'keyboard':true
    });
    $("#ModalBody").text(value);

    var reset = document.getElementById('reset');
    reset.onclick = function(){
         $('#ModalBody').attr('contenteditable',false).css('background-color','#fff');
         $("#ModalBody").text(value);
    };

    $("#ModalBox").one('hide.bs.modal',{target:element},function(event){
        reset.onclick = null;
        var target  = event.data.target;
        var text = $("#ModalBody").text();
        $(target).text(text);
    })
}

function CreateAreaBox(element, value){
    var editState = element.getAttribute("data-EditState");
    if(editState != "true"){
        var areaBox = document.createElement('textarea');
        var name = element.getAttribute("data-name")||element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute('data-name');
        areaBox.className="AreaBox"+"_"+name;
        areaBox.rows = 10;
        //areaBox.width = 40; There is a strange thing
        //areaBox.cols = 100; attr:width and cols don't work, i have no idea about it
        areaBox.style.width = "100%";
        areaBox.style.resize = "none";

        if(!value){
            value = element.getAttribute("data-value");
        }
        areaBox.value = value;

        areaBox.onblur = function (){
            var value = this.value;
            value = value.replace(/</g,'&lt;');
            value = value.replace(/>/g,'&gt;');
            var text = '<pre>' + value + '</pre>';
            CancelEditCell(this.parentNode, this.value, text);
        };
        ClearChild(element);
        element.appendChild(areaBox);
        areaBox.focus();
        element.setAttribute("data-EditState", "true");
        }
    }
//为单元格创建可编辑输入框  
function CreateTextBox(element, value){  
//检查编辑状态，如果已经是编辑状态，跳过  
    var editState = element.getAttribute("data-EditState");
    var name = element.getAttribute("data-name")||element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute('data-name');
    if(editState != "true"){
        var textBox = document.createElement("INPUT");
        textBox.type = "text";
        textBox.className="TextBox"+'_'+name;
        textBox.style.border = "1px solid";
        textBox.style.padding = "0px";
        //以上两行用来 使新生成表单的时候不浮动，更加人性化
        textBox.style.width= (element.parentNode.parentNode.rows[0].cells[element.cellIndex].clientWidth-10)+"px";
        if(!value){
            value = element.getAttribute("data-value");
        }
        textBox.value = value;

        textBox.onblur = function (){
            this.parentNode.setAttribute("data-value", value);
            CancelEditCell(this.parentNode, this.value);
        };

       ClearChild(element);
       element.appendChild(textBox);
       textBox.focus();
       element.setAttribute("data-EditState", "true");
       element.parentNode.parentNode.setAttribute("CurrentRow", element.parentNode.rowIndex);
    }
}

//为单元格创建选择框
function CreateDropDownList(element){
    //检查编辑状态，如果已经是编辑状态，跳过
    var defaultValue = element.getAttribute('data-value')||element.innerHTML;
    element.setAttribute('data-value',defaultValue);
    var name = element.getAttribute("data-name")||element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute('data-name');
    var editState = element.getAttribute("data-EditState");
    if(editState != "true")
    {
        //创建下接框
        var downList = document.createElement("Select");
        downList.className="DropDownList"+"_"+name;
        //添加列表项
        var items = element.getAttribute("data-DataItems");
        if(!items){
            items = element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute("data-DataItems");
        }
        if(items){
            items = eval("[" + items + "]");
            //items example:"{'text':'LINUX',value:'LINUX'},{'text':'WINDOWS',value:'WINDOWS'}"
            for(var i=0; i<items.length; i++){
                var Option = document.createElement("OPTION");
                Option.text = items[i].text;
                Option.value = items[i].value;
                if (items[i].value == defaultValue ){
                    Option.setAttribute('selected','selected')
                }
                downList.options.add(Option);
            }
        }

        //设置创建下接框的失去焦点事件
        downList.onblur = function(){
            CancelEditCell(this.parentNode, this.value, this.options[this.selectedIndex].text);
        };
        //向当前单元格添加创建下接框
        ClearChild(element);
        element.appendChild(downList);
        downList.focus();
        element.setAttribute("data-EditState", "true");
        element.parentNode.parentNode.setAttribute("LastEditRow", element.parentNode.rowIndex);
    }
}

//取消单元格编辑状态  
function CancelEditCell(element, value, text){
    if (element.getAttribute("data-value") != value){
        element.setAttribute("bgcolor", "#FE2E2E");
    }
    element.setAttribute("data-value", value);
    if(text){
       element.innerHTML = text;
    }else{
       element.innerHTML = value;
    }
    element.setAttribute("data-EditState", "false");
    //检查是否有公式计算
    CheckExpression(element.parentNode);
}

//清空指定对象的所有字节点  
function ClearChild(element){element.innerHTML = "";}
  
//添加行  
function AddRow(table, index){
    var lastRow = table.rows[table.rows.length-1];
    var newRow = lastRow.cloneNode(true);
    for(var j=1;j<newRow.cells.length; j++){
        newRow.cells[j].setAttribute("bgcolor", "#FE2E2E");
    }
    table.tBodies[0].appendChild(newRow);
    SetRowCanEdit(newRow);
    return newRow;
}

//删除行  
function DeleteRow(table, index){
    for(var i=table.rows.length - 1; i>0;i--){
        var chkOrder = table.rows[i].cells[0].firstChild;
        if(chkOrder){
            if(chkOrder.type = "CHECKBOX"){
                if(chkOrder.checked){
                 //执行删除
                    table.deleteRow(i);
                }
            }
        }
    }
}

// 编辑行
function EditRow(table){
    for(var i=table.rows.length - 1; i>0;i--){
        var chkOrder = table.rows[i].cells[0].firstChild;
        if(chkOrder){
            if(chkOrder.type = "CHECKBOX"){
                if(chkOrder.checked){
                    var cur_row = table.rows[i];
                    for(var j=1;j<cur_row.cells.length; j++){
                         cur_row.cells[j].setAttribute("bgcolor", "#FE2E2E");
                    }
                    SetRowCanEdit(cur_row);
                }
            }
        }
    }
}

function PublishLua(){
	$.ajax({
        url : '/publish_lua',
        type : 'get',
        data : {},
        dataType:'json',
        success:function(data) {
            setTimeout(function() {
            window.location.reload();
            }, 1200);
        },
        error : function(data) {
            alert('Error:' + data.responseText);
        }
    }); 
}
  
//提取表格的值,JSON格式  
function Save_data(tableobj){  
    var tableData = [];
    for(var i=1; i<tableobj.rows.length;i++){
       tableData.push(GetRowData(tableobj.rows[i]));
    }
    $.ajax({
        url : '/modify_platform',
        type : 'post',
        data : {"data":tableData, "data_len":tableData.length},
        dataType:'json',
        success:function(data) {
            setTimeout(function() {
            document.location.reload();
            }, 1200);
        }
    });
}  
//提取指定行的数据，JSON格式  
function GetRowData(row){  
    var rowData = {};
    for(var j=1;j<row.cells.length; j++){
        var name = row.parentNode.rows[0].cells[j].getAttribute("data-name");
        if(name){
            var isModal = row.cells[j].getAttribute("data-isModal");
            if( isModal == "true"){                          // 这是为了实现modal 而插入的代码，
                var html = row.cells[j].firstChild.innerHTML;//
                html=html.replace(/&lt;/g,'<');              //
                html=html.replace(/&gt;/g,'>');              //
                rowData[name] = html;                        //
                continue;//
            }
            var value = row.cells[j].getAttribute("data-value");
            if(!value){
                value = row.cells[j].innerText;
            }
            rowData[name] = value;
        }
    }
    return rowData;
}  
  
//检查当前数据行中需要运行的字段  
function CheckExpression(row){  
    for(var j=0;j<row.cells.length; j++){
        var expn = row.parentNode.rows[0].cells[j].getAttribute("Expression");
        //如指定了公式则要求计算
        if(expn){
            var format = row.parentNode.rows[0].cells[j].getAttribute("Format");
            if(format){
            //如指定了格式，进行字值格式化
                row.cells[j].innerHTML = formatNumber(Expression(row,expn), format);
            }else{
                row.cells[j].innerHTML = Expression(row,expn);
            }
        }
    }
}
//计算需要运算的字段  
function Expression(row, expn){  
    var rowData = GetRowData(row);
    for(var j=0;j<row.cells.length; j++){
        var name = row.parentNode.rows[0].cells[j].getAttribute("data-name");
        if(name){
           var reg = new RegExp(name, "i");
           expn = expn.replace(reg, rowData[name].replace(/,/g, ""));
        }
    }
    return eval(expn);
}  
  
///////////////////////////////////////////////////////////////////////////////////
/** 
* 格式化数字显示方式   
* 用法 
* formatNumber(12345.999,'#,##0.00'); 
* formatNumber(12345.999,'#,##0.##'); 
* formatNumber(123,'000000'); 
* @param num 
* @param pattern 
*/  
/* 以下是范例 
formatNumber('','')=0 
formatNumber(123456789012.129,null)=123456789012 
formatNumber(null,null)=0 
formatNumber(123456789012.129,'#,##0.00')=123,456,789,012.12 
formatNumber(123456789012.129,'#,##0.##')=123,456,789,012.12 
formatNumber(123456789012.129,'#0.00')=123,456,789,012.12 
formatNumber(123456789012.129,'#0.##')=123,456,789,012.12 
formatNumber(12.129,'0.00')=12.12 
formatNumber(12.129,'0.##')=12.12 
formatNumber(12,'00000')=00012 
formatNumber(12,'#.##')=12 
formatNumber(12,'#.00')=12.00 
formatNumber(0,'#.##')=0 
*/  
function formatNumber(num,pattern){    
var strarr = num?num.toString().split('.'):['0'];    
var fmtarr = pattern?pattern.split('.'):[''];    
var retstr='';    
    
// 整数部分    
var str = strarr[0];    
var fmt = fmtarr[0];    
var i = str.length-1;      
var comma = false;    
for(var f=fmt.length-1;f>=0;f--){    
    switch(fmt.substr(f,1)){    
      case '#':    
        if(i>=0 ) retstr = str.substr(i--,1) + retstr;    
        break;    
      case '0':    
        if(i>=0) retstr = str.substr(i--,1) + retstr;    
        else retstr = '0' + retstr;    
        break;    
      case ',':    
        comma = true;    
        retstr=','+retstr;    
        break;    
    }    
}    
if(i>=0){    
    if(comma){    
      var l = str.length;    
      for(;i>=0;i--){    
        retstr = str.substr(i,1) + retstr;    
        if(i>0 && ((l-i)%3)==0) retstr = ',' + retstr;     
      }    
    }    
    else retstr = str.substr(0,i+1) + retstr;    
}    
    
retstr = retstr+'.';    
// 处理小数部分    
str=strarr.length>1?strarr[1]:'';    
fmt=fmtarr.length>1?fmtarr[1]:'';    
i=0;    
for(var f=0;f<fmt.length;f++){    
    switch(fmt.substr(f,1)){    
      case '#':    
        if(i<str.length) retstr+=str.substr(i++,1);    
        break;    
      case '0':    
        if(i<str.length) retstr+= str.substr(i++,1);    
        else retstr+='0';    
        break;    
    }    
}    
return retstr.replace(/^,+/,'').replace(/\.$/,'');    
}
