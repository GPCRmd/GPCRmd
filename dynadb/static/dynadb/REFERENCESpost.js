

$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };


    $("#id_submit").click(function(event) {
        event.preventDefault();
	var self = $(this);
        var protform = $(this).parents("#myformRef");
        var submission_id=$(protform).find("#submission_id").val()
        //var file_source=modelform.find("#file_source");
        //fields.set_readonly_color();
        var buttons = $("button,input[type='submit'],input[type='button']");

        self.prop('disabled',true);
        buttons.prop('disabled',true);
        //file_source.prop('disabled',true);
        
        $(protform).ajaxSubmit({
            url: "./",
            type: 'POST',
            dataType:'text',
            success: function(data) {
                console.log(data);
                //var urllist=window.location.href.split("/");
                alert("Congratulations!! "+data);
                window.location.replace("../references/");
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
