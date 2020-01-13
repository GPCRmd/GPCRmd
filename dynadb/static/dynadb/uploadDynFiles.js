$(document).ready(function() {
    $.fn.exists = function () {
      return this.length !== 0;
    }


    function adjust_iframe_height_from_child(iframe_id) {
        //if compatible or non-cross origin 
        if ( window.parent.document != null) {
            var current_iframe = $(window.parent.document).find(iframe_id);
            if (current_iframe.exists()) {
                var body_height = $(document).find("body").height();
                current_iframe.height(body_height);
            }
        }                                                                                                                                                      
    }
    
    var upload_button_jquery_selector = "[id^=id_][id$=_upload]";
    var file_type = $(upload_button_jquery_selector).attr('id').split('_')[1];
    var iframe_id = "#id_"+file_type+"_iframe";
    adjust_iframe_height_from_child(iframe_id);


    $(upload_button_jquery_selector).click(function(event) {
        var self = $(this);
        event.preventDefault();
        var file_type = self.attr('id').split('_')[1];
        var iframe_id = "#id_"+file_type+"_iframe";
        var dynform = $(this).parents("#upload_dynform");
        var download_file = dynform.find("[id|='id_"+file_type+"_download_url']");
        var no_js = dynform.find("input[name='no_js']");
        no_js.val(0);
        var link_div = dynform.find("#id_"+file_type+"_download_url_div");
        var link_div_parent = link_div.parent();
        
        link_div.hide();
        
        self.prop('disabled',true);
        if (file_type == "traj") {
            var maxsize = "8 GB";
        } else {
            var maxsize = "50 MB";
        }
        
        $(dynform).ajaxSubmit({
            url: "./",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert(data.msg);
                var i = 0;
                var download_url_file = data.download_url_file;
                $("[id^=id_"+file_type+"_download_url_div-]").remove();
                if (download_url_file.length == 1) {
                    download_url_file = download_url_file[0]
                }
                if (typeof download_url_file === 'string') {
                    download_file.attr('href',download_url_file);
                    download_file.show();
                    link_div.show();
                } else {
                    $(download_url_file).each(function() {
                        var link_div_new = link_div.clone();
                        link_div_new.attr('id',link_div_new.attr('id')+"-"+i.toString());
                        var download_file_new = link_div_new.find("[id|='id_"+file_type+"_download_url']");
                        download_file_new.attr('id',download_file.attr('id')+"-"+i.toString());
                        download_file_new.attr('href',this);
                        download_file_new.text(download_file_new.text().replace("file","file "+(i+1).toString()));
                        download_file_new.show();
                        link_div_new.show();
                        link_div_parent.append(link_div_new);
                        i++;
                    });
                    
                    

                    
                    
                    

                }
               
                
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    var responsetext = xhr.responseText;
                    $("[id^=id_"+file_type+"_download_url_div-]").remove();
                    download_file.hide();
                    if (xhr.status == 432) {
                        $("[id^=id_"+file_type+"_download_url_div-]").remove();
                    } else if (xhr.status==413 && /text\/html/.test(xhr.getResponseHeader("content-type"))) {
                        var responsetext = 'Request body (including files) too large.';
                    } else if (xhr.status==500 && /text\/html/.test(xhr.getResponseHeader("content-type"))) {
                        var responsetext = 'Apache server error. Please, check that your upload does not exceed file size or number of files limits.';
                    }
                    alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+responsetext);
                }
                else if (xhr.readyState == 0) {
                    alert("Connection error. Please, try later and check that your file is not larger than "+maxsize+".");
                }
                else {
                    alert("Unknown error");
                    $("[id^=id_"+file_type+"_download_url_div-]").remove();
                    download_file.hide();
                }
            },
            complete: function(xhr,status,msg){
                self.prop('disabled',false);
                
                adjust_iframe_height_from_child(iframe_id);
            }
        });
    });   
});
