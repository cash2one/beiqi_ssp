/**
 * Created by Jay on 2015-11-2.
 */

SmartHome.Common.Form.serialize = function(form){
    // 表单序列化
    var output = [];
    var elements = form.elements;
    var optValue;
    for (var index= 0 ,length = elements.length;index<length;index++){
        var field = elements[index];
        if(field.name.length){
            switch (field.type){
                case 'select-one':
                case 'select-multiple':
                    for(var j= 0,optLen = field.options.length;j<optLen;j++){
                        var option = field.options[j];
                        if (option.selected){
                            optValue = option.value || option.text;
                            // 简单写，可能不兼容低IE
                            output.push(encodeURIComponent(option.name)+"="+encodeURIComponent(optValue))
                        }

                    }
                    break;
                case 'checkbox':
                case 'radio':
                    if(field.checked){
                        optValue = option.value || option.text;
                        output.push(encodeURIComponent(option.name)+"="+encodeURIComponent(optValue))
                    }
                    break;
                case 'undefined':
                case 'file':
                case 'reset':
                case 'button':
                case 'submit':
                    break;
                default :
                    output.push(encodeURIComponent(field.name)+"="+encodeURIComponent(field.value))
            }
        }
    }
    return output.join("&")
};

SmartHome.Common.resetForm = function(form){
    // 重置所有表单
    var elements = form.elements;
    for(var index= 0,length = elements.length;index<length;index++){
        var field = elements[index];
        if (field.name.length){
            switch (field.type){
                case 'text':
                case 'password':
                    field.value='';
                    break;
            }
        }
    }

};