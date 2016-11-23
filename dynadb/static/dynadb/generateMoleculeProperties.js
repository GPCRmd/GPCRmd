var uploadmol1_global_html = '';
var uploadmol2_global_html = '';

$(document).ready(function() {
    $.fn.exists = function () {
        return this.length !== 0;
    };
    
    uploadmol1_global_html = $("[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1']").clone();
    uploadmol2_global_html = $("[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2']").clone();
    $(document).on('click',"[id='id_upload_button'],[id|=id_form][id$='-upload_button']",function(){
        var max_size = 52428800;
        var pngsize = 300;
        var molform = $(this).parents("[id|=molform]");
        var uploadmol1 = $(molform).find("[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1']");
        var uploadmol1_html = $(uploadmol1_global_html).clone();
        uploadmol1_html.attr('id',uploadmol1.attr('id'));
        uploadmol1_html.attr('name',uploadmol1.attr('name'));
        var uploadmol2 = $(molform).find("[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2']");
        var uploadmol2_html = $(uploadmol2_global_html).clone();
        uploadmol2_html.attr('id',uploadmol2.attr('id'));
        uploadmol2_html.attr('name',uploadmol2.attr('name'));
        var self = $(this);
        $(self).prop('disabled',true);
        var currentform = $(molform).find("#small_molecule");
        var molformid = $(molform).attr('id');
        var logfile = $(molform).find("[id='id_logfile'],[id|=id_form][id$='-logfile']");
        var inchi = $(molform).find("[id='id_inchi'],[id|=id_form][id$='-inchi']");
        var inchikey = $(molform).find("[id='id_inchikey'],[id|=id_form][id$='-inchikey']");
        var sinchikey = $(molform).find("[id='id_sinchikey'],[id|=id_form][id$='-sinchikey']");
        var net_charge = $(molform).find("[id='id_net_charge'],[id|=id_form][id$='-net_charge']");
        var smiles = $(molform).find("[id='id_smiles'],[id|=id_form][id$='-smiles']");
        
        var molsdf = $(molform).find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']");
        
        
        if ($(molsdf).val() == "") {
             $(self).prop('disabled',false);
             alert("No file selected.");
             return false;
        }
        
        var extension = $(molsdf).val().substr( ($(molsdf).val().lastIndexOf('.') +1) ).toLowerCase();
        switch(extension) {
             case "mol":
             case "sdf":
             case "sd":
             break;
             default:
                $(self).prop('disabled',false);
                alert("Invalid extension.");
                return false;
        }
        
        
        
        if ($(molsdf)[0].hasOwnProperty('files') && typeof molsdf[0].files[0] !== 'undefined' && molsdf[0].files[0].hasOwnProperty('size')) {
            if (molsdf[0].files[0].size > max_size) {
                $(self).prop('disabled',false);
                alert("Maximum size is 50 MB.");
                return false;
            }
        }
        
        inchi.val('');
        inchikey.val('');
        sinchikey.val('');
        net_charge.val('');
        smiles.val('');
        self.resetCompoundInfo();
        
        
        var molsdfname = $(molsdf).attr('name');
        $(currentform).ajaxSubmit({
            url: "./generate_properties/",
            type: 'POST',
            data: {'molpostkey':molsdfname,'pngsize':pngsize},
            dataType:'json',
            success: function(data) {

                
                inchi.val(data.inchi.inchi);
                inchikey.val(data.inchikey);
                sinchikey.val(data.sinchikey);
                net_charge.val(data.charge);
                smiles.val(data.smiles);
                
                var newuploadmol = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(uploadmol1).attr("id"))
                .attr("name",$(uploadmol1).attr("name"))
                .attr("height",pngsize)
                .attr("width",pngsize);
                $(uploadmol1).replaceWith($(newuploadmol));
                logfile.attr("href",data.download_url_log);
                logfile.show();
                uploadmol1 = $(newuploadmol);
                newuploadmol = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(uploadmol2).attr("id"))
                .attr("name",$(uploadmol2).attr("name"))
                .attr("height",pngsize)
                .attr("width",pngsize);
                $(uploadmol2).replaceWith($(newuploadmol));
                logfile.attr("href",data.download_url_log);
                logfile.show();
                uploadmol2 = $(newuploadmol);
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    
                    if (xhr.status==422) {
                        var data = jQuery.parseJSON(xhr.responseText);
                        if (data.download_url_log != null) {
                            logfile.attr("href",data.download_url_log);
                            logfile.show();
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
                $(self).prop('disabled',false);

            }
        });
    });
        
});