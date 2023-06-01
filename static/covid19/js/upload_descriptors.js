$(document).ready(function() {
    document.domain=document.domain;


    $("#submit_upload").click(function(event) {
        var self = $(this);
        event.preventDefault();
        var dynform = $(this).parents("form");
        $(this).addClass("disabled")
        $("#loading_custom").css("display","inline")
        
        var error_c=$("#form_error");
        error_c.css("display","none")
        $(dynform).ajaxSubmit({
            url: "./",
            type: 'POST',
            dataType:'json',
            success: function(data) {  
                parent.added_custom_descr(data.impact_per_var,data.added_metrics)                
            },
            error: function(xhr,status,msg){
                var error_msg="Unknown error";
                if (xhr.readyState == 4) {
                    error_msg=msg;
                }
                else if (xhr.readyState == 0) {
                    error_msg="Connection error. Please, try again later."
                }
                error_c.find(".error_msg").text(error_msg)
                error_c.css("display","inline");

            },
            complete: function(xhr,status,msg){
                //self.prop('disabled',false);
                $("#submit_upload").removeClass("disabled")
                $("#loading_custom").css("display","none")
                
            }
        });
    });   


})