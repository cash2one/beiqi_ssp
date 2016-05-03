function GetRandomNum()
{
var Range = 2000000000;
var Rand = Math.random();
return Math.round(Rand*Range);
}

function reinitIframe(frameId) {
    var iframe = document.getElementById(frameId);
    try {
        var bHeight = iframe.contentWindow.document.body.scrollHeight;
        var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
        var selfHeight = iframe.height;
        var height = Math.max(bHeight, dHeight);
        iframe.height = height;
        fixParentHeight(frameId, 'mainFrame');
    } catch (ex) {
    }
}

function fixParentHeight(childId, parentId) {
    if (this.parent.document.getElementById(parentId).scrollHeight < document.getElementById(childId).height) {
        this.parent.document.getElementById(parentId).height = document.getElementById(childId).height;
    }
}

function activeMe(index) {
    $('ul li').each(function(id) {
        $('ul li')[id].removeClass('active');
    });
    $($('ul li')[index-1]).addClass('active');
}


function SaveTableToUrl(table,url){
    var tableData = new Array();
    for(var i=1; i<table.rows.length;i++){
        var row_data = GetRowData(table.rows[i]);
        //console.log("row_data!!!!" + JSON.stringify(row_data));
        tableData.push(row_data);
    }

    $.ajax({
        url : url,
        type : 'post',
        data : {"js_data":JSON.stringify(tableData)},
        dataType:'text',
        success:function(data,textStatus,jqXHRa){
            setTimeout(function(){
            window.location.reload();
            },500);
        },
        error : function(XMLHttpRequest, textStatus, errorThrown) {
            alert('Error:' + textStatus + errorThrown);
        }
    });
}

