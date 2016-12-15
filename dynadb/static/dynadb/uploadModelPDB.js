$(document).ready(function() {
    
    $("#id_upload_pdb").click(function() {
        var self = $(this);
        var modelform = $(this).parents("#myform");
        var download_pdb = modelform.find('#id_download_pdb');
        self.prop('disabled',true);

        $(modelform).ajaxSubmit({
            url: "./upload_model_pdb/",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert(data.msg);
                download_pdb.attr('href',data.download_url_pdb);
                download_pdb.show();
                
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
                    download_pdb.hide();
                }
                else if (xhr.readyState == 0) {
                    alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
                }
                else {
                    alert("Unknown error");
                    download_pdb.hide();
                }
            },
            complete: function(xhr,status,msg){
                self.prop('disabled',false);

            }
        });
    });   
});