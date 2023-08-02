

$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };


    $("#id_submit").click(function(event) {
        event.preventDefault();
	    var self = $(this);
        var urllist=window.location.pathname.split("/");
        if (urllist.length ==6){ // /dynadb/moleculereuse/100/68/  --> [ "", "dynadb", "moleculereuse", "100", "68", ""] 6 elements
            var submission_id=urllist[urllist.length-3];
            var model_id=urllist[urllist.length-2];
            var url_post="../../../modelreuse/"+submission_id+"/"+model_id+"/";
            var url_success="../../../dynamicsreuse/"+submission_id+"/"+model_id+"/";
            var modelformdom=$(document).find("[id='Choose_reused_model_1']");
            var key=$(modelformdom).attr('name');
            var modelform={};
            modelform[key]=$(modelformdom).val();
            var file_source=$(document).find("#file_source");
            var buttons = $("button,input[type='submit'],input[type='button']");
        }else{
            var submission_id=urllist[urllist.length-2];
            var url_post="./";
            var url_success="../../dynamics/"+submission_id+"/";
            var modelform = $(this).parents("#myform");
            var file_source=$(modelform).find("#file_source");
            var buttons = $("button,input[type='submit'],input[type='button']");
        }
        //fields.set_readonly_color();

        self.prop('disabled',true);
        buttons.prop('disabled',true);
        file_source.prop('disabled',true);
        if (urllist.length ==8){ // http://localhost:8000/dynadb/moleculereuse/100/68/  --> ["http:", "", "localhost:8000", "dynadb", "moleculereuse", "100", "68", ""] 8 elements
            $.ajax({
                data:modelform,
                url: url_post,
                type: 'POST',
                dataType:'text',
                success: function(data) {
                    alert("Congratulations!! "+data);
                    window.location.replace(url_success);
                    
                },
                error: function(xhr,status,msg){
                    if (xhr.readyState == 4) {
                        alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
                    }
                    else if (xhr.readyState == 0) {
                        alert("Connection error. Please, try later.");
                    }
                    else {
                        alert("Unknown error");
                    }
                },
                complete: function(xhr,status,msg){
                    buttons.prop('disabled',false);
                    file_source.prop('disabled',false);
                    self.prop('disabled',false);
                }
            });
        }else{
            $(modelform).ajaxSubmit({
              //  data:modelform,
                url: url_post,
                type: 'POST',
                dataType:'text',
                success: function(data) {
                    alert("Congratulations!! "+data);
                    window.location.replace(url_success);
                    
                },
                error: function(xhr,status,msg){
                    if (xhr.readyState == 4) {
                        alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
                    }
                    else if (xhr.readyState == 0) {
                        alert("Connection error. Please, try later.");
                    }
                    else {
                        alert("Unknown error");
                    }
                },
                complete: function(xhr,status,msg){
                    buttons.prop('disabled',false);
                    file_source.prop('disabled',false);
                    self.prop('disabled',false);
                }
            });
         }
    
    
    
    });


});
