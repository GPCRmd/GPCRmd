$(document).ready(function() {
    $("#id_check_pdb_mol").click(function() {
        var self = $(this);
        var modelform = $(this).parents("#myform");
        var fields = modelform.find("#pElement2 :input");
        var buttonadd = modelform.find("#id_add_button");
        var buttondel = modelform.find("#id_del_button");
        fields.prop('disabled',true);
        self.prop('disabled',true);
        buttonadd.prop('disabled',true);
        buttondel.prop('disabled',true);
        $(modelform).ajaxSubmit({
            url: "./check_pdb_molecules/",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert(data.msg);
                
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    
                    if (xhr.status==422) {
                        var data = jQuery.parseJSON(xhr.responseText);
                        if (data.download_url_log != null) {
//                             logfile.attr("href",data.download_url_log);
//                             logfile.show();
                        }
                        var responsetext = data.msg;
                    } else {
                        var responsetext = xhr.responseText;
                    }
                    alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+responsetext);
                }
                else if (xhr.readyState == 0) {
                    alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
                }
                else {
                    alert("Unknown error");
                }
            },
            complete: function(xhr,status,msg){
                self.prop('disabled',false);
                fields.prop('disabled',false);
                buttonadd.prop('disabled',false);
                buttondel.prop('disabled',false);
            }
        });
    
    
    
    
    });
    
    
    
});