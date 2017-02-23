

$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };


    $("#id_submit").click(function(event) {
        event.preventDefault();
	var self = $(this);
        var dynform = $(this).parents("#myformDyn");
        //var file_source=modelform.find("#file_source");
        //fields.set_readonly_color();
        var buttons = $("button,input[type='submit'],input[type='button']");

        self.prop('disabled',true);
        buttons.prop('disabled',true);
        //file_source.prop('disabled',true);
        var urllist=window.location.href.split("/");
         
        if (urllist.length ==8){ // http://localhost:8000/dynadb/moleculereuse/100/68/  --> ["http:", "", "localhost:8000", "dynadb", "moleculereuse", "100", "68", ""] 8 elements
            var submission_id=urllist[urllist.length-3];
            var model_id=urllist[urllist.length-2];
            var url_post="./";
            var url_success="../../../submission_summary/"+submission_id+"/";
            console.log(urllist.length)
        }else{
            var submission_id=urllist[urllist.length-2];
            var url_post="./";
            var url_success="../../submission_summary/"+submission_id+"/";
            console.log(urllist.length+" lll")
        }
        $(dynform).ajaxSubmit({
            url: "./",
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
                //file_source.prop('disabled',false);
                self.prop('disabled',false);
            }
        });
    
    
    
    
    });


});
